import time
import json
import struct
from queue import Queue
from flask import Flask, jsonify, abort, make_response, request, url_for, render_template, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

from camera_pi import Camera
from buttons import ButtonCollection, Button

auth = HTTPBasicAuth()
app = Flask(__name__)

ROBOT_USER = "robot"

users = {
    "user": generate_password_hash("something"),
    ROBOT_USER: generate_password_hash("naboris")
}

command_queue = Queue()

start_header = b'\xbb\x08'
message_start_header = b'\xde\xad\xbe\xef'

commands = ButtonCollection(
    Button("spin left", "l", "spin_left_button", "command_button drive"),
    Button("spin right", "r", "spin_right_button", "command_button drive"),
    Button("drive forward", "d 0", "drive_forward_button", "command_button drive"),
    Button("drive left", "d 90 150", "drive_left_button", "command_button drive"),
    Button("drive backward", "d 180", "drive_backward_button", "command_button drive"),
    Button("drive right", "d 270 150", "drive_right_button", "command_button drive"),
    Button("stop", "s", "stop_driving_button", "command_button drive"),

    Button(["lights on", "lights off"], "toggle_lights", "toggle_lights_button", "command_button toggles",
           int(False)),  # TODO: replace with contents of status
    Button("take a photo", "photo", "take_a_photo_button", "command_button toggles"),
    Button(["pause video", "unpause video"], "toggle_camera", "toggle_camera_button",
           "command_button toggles"),
    Button(["start recording", "stop recording"], "toggle_recording", "toggle_recording_button",
           "command_button toggles", int(False)),  # TODO: replace with contents of status

    Button("say hello!", "hello", "say hello button", "command_button speak"),
    Button("PANIC!!!", "alert", "alert button", "command_button speak"),
)

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/')
@auth.login_required
def index_page():
    """Page for viewing the camera feed and sending commands to the robot"""
    return render_template('index.html', commands=commands)


@app.route('/status')
@auth.login_required
def status_page():
    """Page for checking the general status of the robot"""
    return render_template('status-page.html')


@app.route('/cmd', methods=['PUT'])
@auth.login_required
def put_command():
    """Put a command to send to the robot"""
    print("putting:", request.json)
    command_timestamp = struct.pack('d', time.time())
    command_queue.put((command_timestamp, request.json))
    return make_response("", 200)

def command_queue_generator(generator_queue):
    yield start_header

    while True:
        with app.app_context():
            # result = ""
            # if generator_queue.empty():
            #     result = ";\n"
            #     time.sleep(0.1)
            # else:
            #     while not generator_queue.empty():
            #         timestamp, command_json = generator_queue.get()
            #         result += "%s-%s;\n" % (timestamp, command_json["command"])

            if not generator_queue.empty():
                command_timestamp, command_json = generator_queue.get()
                result = command_timestamp + command_json["command"].encode()
                len_result_bytes = len(result).to_bytes(4, 'big')
                batch_timestamp = struct.pack('d', time.time())
                result = message_start_header + len_result_bytes + batch_timestamp + result
                print("sending '%s':" % command_json["command"])
                print(result)
                yield result
            # else:
            #     yield message_start_header + b"\x00\x00\x00\x00"
            #     time.sleep(0.01)


@app.route('/cmd', methods=['GET'])
@auth.login_required
def get_command():
    """Function for the robot. Retrieve command to execute"""
    if auth.username() == ROBOT_USER:
        return Response(command_queue_generator(command_queue), mimetype='text/json')
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/api', methods=['GET'])
@auth.login_required
def get_api():
    """List all the properties and functions of the api"""
    return jsonify()


@app.route('/api/robot/status', methods=['PUT'])
@auth.login_required
def set_status():
    """Function for the robot. Update the robot's current status"""
    if auth.username() == ROBOT_USER:
        return jsonify()
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

def frame_generator(picamera):
    """Camera frame generator"""
    print("streaming images")
    while True:
        frame = picamera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.5 / picamera.camera.framerate)


def frame_generator_with_meta(picamera):
    """Camera frame generator"""
    print("streaming images with info")
    yield start_header

    while True:
        timestamp = time.time()
        timestamp_bytes = struct.pack('d', timestamp)

        width = int(picamera.camera.resolution[0])
        height = int(picamera.camera.resolution[1])

        width_bytes = width.to_bytes(2, 'big')
        height_bytes = height.to_bytes(2, 'big')

        frame = picamera.get_frame()
        len_frame_bytes = len(frame).to_bytes(4, 'big')

        yield (message_start_header +
                   len_frame_bytes + frame + timestamp_bytes + width_bytes + height_bytes +
               b'\r\n')
        time.sleep(0.5 / picamera.camera.framerate)


@app.route('/api/robot/rightcam', methods=['GET'])
@auth.login_required
def get_camera():
    """Stream frames from the right camera to the client"""
    return Response(frame_generator(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/robot/rightcam_meta', methods=['GET'])
@auth.login_required
def get_camera_with_meta():
    """Stream frames from the right camera to the client"""
    if auth.username() == ROBOT_USER:
        return Response(frame_generator_with_meta(Camera()))
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/robot/imu', methods=['PUT'])
@auth.login_required
def put_imu():
    """Function for the robot. Update the IMU's data on the server"""
    if auth.username() == ROBOT_USER:
        return jsonify()
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/robot/trajectory', methods=['PUT'])
@auth.login_required
def put_trajectory():
    """Function for the robot. Update the trajectory on the server according to the current algorithm in use"""
    if auth.username() == ROBOT_USER:
        return jsonify()
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/robot/sound', methods=['POST'])
@auth.login_required
def post_sound():
    """Function for the robot. Update the list of sounds"""
    if auth.username() == ROBOT_USER:
        return jsonify()
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/robot/sound', methods=['PUT'])
@auth.login_required
def put_sound():
    """Function for the robot. Update the list of sounds"""
    if auth.username() == ROBOT_USER:
        return jsonify()
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/robot/move_command', methods=['POST'])
@auth.login_required
def post_move_command():
    """Function for the robot. Update the list of move commands"""
    if auth.username() == ROBOT_USER:
        return jsonify()
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/robot/move_command', methods=['PUT'])
@auth.login_required
def put_move_command():
    """Function for the robot. Update the list of move commands"""
    if auth.username() == ROBOT_USER:
        return jsonify()
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/robot/look', methods=['POST'])
@auth.login_required
def post_turret():
    """Function for the robot. Update the list of looking commands"""
    return jsonify()

@app.route('/api/robot/look', methods=['PUT'])
@auth.login_required
def put_turret():
    """Function for the robot. Update the list of looking commands"""
    return jsonify()


@app.errorhandler(404)
@auth.login_required
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, threaded=True)
