import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):
    @classmethod
    def frames(cls):
        with picamera.PiCamera() as camera:
            # camera.resolution = (640, 480)
            camera.resolution = (720, 480)
            camera.framerate = 60.0
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
