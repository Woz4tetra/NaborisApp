from flask import Flask, jsonify, abort, make_response, request, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)

ROBOT_USER = "robot"

users = {
    "user": generate_password_hash("something")
    ROBOT_USER: generate_password_hash("naboris")
}

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
    return render_template('index.html')


@app.route('/status')
@auth.login_required
def status_page():
    """Page for checking the general status of the robot"""
    return render_template('status-page.html')


@app.route('/cmd', methods=['PUT'])
@auth.login_required
def put_command():
    """Put a command to send to the robot"""
    return jsonify()


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


def frame_generator(camera):
    """Camera frame generator"""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/api/robot/rightcam', methods=['GET'])
@auth.login_required
def get_camera():
    """Stream frames from the right camera to the client"""
    return Response(frame_generator(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


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
    app.run(host="0.0.0.0", debug=True, threaded=True)
