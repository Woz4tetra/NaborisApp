import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):
    @classmethod
    def frames(cls):
        with picamera.PiCamera() as camera:
            # camera.resolution = (640, 480)
            # camera.resolution = (720, 480)
            camera.resolution = (410, 308)
            camera.framerate = 30.0
            camera.exposure_mode = "antishake"
            camera.shutter_speed = 0
            camera.brightness = 50
            camera.iso = 400
            camera.awb_mode = "auto"

            # let camera warm up
            time.sleep(2)
            cls.camera = camera

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
