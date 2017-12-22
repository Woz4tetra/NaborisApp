import time
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
    command_queue.put(request.json)
    return request.json, 200, {'Content-Type': 'text/plain'}

@app.route('/cmd', methods=['GET'])
@auth.login_required
def get_command():
    """Function for the robot. Retrieve command to execute"""
    if auth.username() == ROBOT_USER:
        return jsonify(command_queue.get())


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
    yield b'\xbb\x08'

    while True:
        timestamp = time.time()
        timestamp_bytes = struct.pack('d', timestamp)

        width = int(picamera.camera.resolution[0])
        height = int(picamera.camera.resolution[1])

        width_bytes = width.to_bytes(2, 'big')
        height_bytes = height.to_bytes(2, 'big')

        frame = picamera.get_frame()
        len_frame_bytes = len(frame).to_bytes(4, 'big')

        yield (b'\xde\xad\xbe\xef' +
                   len_frame_bytes + frame + timestamp_bytes + width_bytes + height_bytes +
               b'\r\n')
        time.sleep(0.5 / picamera.camera.framerate)


def timestamp_generator():
    while True:
        timestamp = time.time()

        timestamp_bytes = struct.pack('d', timestamp)
        yield b'\xff\xd8' + timestamp_bytes + b'\xff\xd9'
        time.sleep(0.0167)

@app.route('/api/robot/timestamp', methods=['GET'])
@auth.login_required
def get_timestamp():
    """Stream frames from the right camera to the client"""
    return Response(timestamp_generator())


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


@app.route('/api/robot/imu', methods=['PUT'])
@auth.login_required
def put_imu():
    """Function for the robot. Update the IMU's data on the server"""
    if auth.username() == ROBOT_USER:
        return jsonify()


@app.route('/api/robot/trajectory', methods=['PUT'])
@auth.login_required
def put_trajectory():
    """Function for the robot. Update the trajectory on the server according to the current algorithm in use"""
    if auth.username() == ROBOT_USER:
        return jsonify()


@app.route('/api/robot/sound', methods=['POST'])
@auth.login_required
def post_sound():
    """Function for the robot. Update the list of sounds"""
    if auth.username() == ROBOT_USER:
        return jsonify()


@app.route('/api/robot/sound', methods=['PUT'])
@auth.login_required
def put_sound():
    """Function for the robot. Update the list of sounds"""
    if auth.username() == ROBOT_USER:
        return jsonify()


@app.route('/api/robot/move_command', methods=['POST'])
@auth.login_required
def post_move_command():
    """Function for the robot. Update the list of move commands"""
    if auth.username() == ROBOT_USER:
        return jsonify()


@app.route('/api/robot/move_command', methods=['PUT'])
@auth.login_required
def put_move_command():
    """Function for the robot. Update the list of move commands"""
    if auth.username() == ROBOT_USER:
        return jsonify()


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
