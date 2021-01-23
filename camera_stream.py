import cv2 as cv
import numpy as np
from threading import Thread, Lock
import time

class CameraStream():
    def __init__(self):
        self.camera = cv.VideoCapture(0)
        
        self.camera.set(cv.CAP_PROP_FRAME_WIDTH, 640) # Width
        self.camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480) # Height
        self.camera.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M','J','P','G'))
        self.camera.set(cv.CAP_PROP_FPS, 15) # FPS

        #self.camera.set(cv.CAP_PROP_BRIGHTNESS, 1) # Brightness
        #self.camera.set(cv.CAP_PROP_CONTRAST, 0.75) # Contrast
        #self.camera.set(cv.CAP_PROP_SATURATION, 0.75) # Saturation
        #self.camera.set(cv.CAP_PROP_HUE, 1) # Hue
        #self.camera.set(cv.CAP_PROP_GAIN, 1) # Gain
        #self.camera.set(cv.CAP_PROP_EXPOSURE, 0.5) # Exposure

    def start(self):
        self.success = None
        self.frame = None

        self.read_lock = Lock()

        self.stop_thread = False
        self.thread = Thread(target=self.__update)
        self.thread.start()
    
    def __update(self):
        while not self.stop_thread:
            success, frame = self.camera.read()

            self.read_lock.acquire()
            self.success, self.frame = success, frame
            self.read_lock.release()
    
    def frame_generator(self):
        try:
            while self.success is None or self.frame is None:
                pass
            
            while not self.stop_thread:
                self.read_lock.acquire()
                success, frame = self.success, self.frame.copy()
                self.read_lock.release()

                if not success:
                    print("Unable to get frame from camera.")
                    self.terminate()
                    break
                else:
                    buffer = cv.imencode(".jpg", frame)[1]
                    frame = buffer.tobytes()

                    yield (b'--frame\r\n' +
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    
                    time.sleep(0.05)
        except GeneratorExit:
            print("Generator closed!")
            self.terminate()
    
    def old_frame_generator(self):
        try:
            while True:
                success, frame = self.camera.read()

                if not success:
                    print("Unable to get frame from camera.")
                    self.old_terminate()
                    break
                else:
                    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

                    lower_red = np.array([6, 100, 50])
                    upper_red = np.array([172, 165, 100])
                    
                    mask_frame = cv.bitwise_not(cv.inRange(hsv_frame, lower_red, upper_red))

                    result_frame = cv.bitwise_and(frame, frame, mask=mask_frame)

                    buffer = cv.imencode(".jpg", result_frame)[1]
                    frame = buffer.tobytes()

                    yield (b'--frame\r\n' +
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except GeneratorExit:
            print("Generator closed!")
            self.old_terminate()
    
    def terminate(self):
        self.stop_thread = True
        
        self.thread.join()
        self.camera.release()
        cv.destroyAllWindows()
    
    def old_terminate(self):
        self.camera.release()
        cv.destroyAllWindows()
    
    def __del__(self):
        #self.terminate()
        self.old_terminate()