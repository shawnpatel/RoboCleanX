import io
import picamera
import logging
from threading import Thread, Condition

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class Stream(object):
    def start_recording(self):
        with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
            self.camera = camera
            self.output = StreamingOutput()
            self.camera.start_recording(self.output, format='mjpeg')        
    
    def frame_generator(self):
        try:
            while True:
                with self.output.condition:
                    self.output.condition.wait()
                    frame = self.output.frame
                    yield(b'--FRAME\r\n' +
                          b'Content-Type: image/jpeg\r\n\r\n' + 
                          frame + b'\r\n')
        except Exception as e:
            logging.warning('Removed streaming client %s: %s', self.client_address, str(e))