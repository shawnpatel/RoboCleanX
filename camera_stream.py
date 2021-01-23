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
                    frame = self.__process_image(frame)
                    buffer = cv.imencode(".jpg", frame)[1]
                    frame = buffer.tobytes()

                    yield (b'--frame\r\n' +
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except GeneratorExit:
            print("Generator closed!")
            self.old_terminate()
    
    def __is_bad_contour(self, contour):
        area = cv.contourArea(contour)
        peri = cv.arcLength(contour, True)
        approx_poly = cv.approxPolyDP(contour, 0.02 * peri, True)
        rotated_rect = rect = cv.minAreaRect(contour)

        if area < 500:
            return True
        elif len(approx_poly) > 10:
            return True
        elif rotated_rect.angle > 5 or rotatted_rect.angle < -5:
            return True
        
        return False

    def __process_image(self, frame):
        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        lower_red = np.array([6, 0, 0])
        upper_red = np.array([172, 255, 255])
        
        hsv_mask = cv.bitwise_not(cv.inRange(hsv_frame, lower_red, upper_red))

        contours, hierarchy = cv.findContours(hsv_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        bad_contours_mask = np.ones(frame.shape[:2], dtype="uint8") * 255

        bad_contours = []
        good_contours = []
        for contour in contours:
            if self.__is_bad_contour(contour):
                bad_contours.append(contour)
            else:
                good_contours.append(contour)
                
        cv.drawContours(bad_contours_mask, bad_contours, -1, 0, -1)

        result_frame = cv.bitwise_and(frame, frame, mask=hsv_mask)
        result_frame = cv.bitwise_and(result_frame, result_frame, mask=bad_contours_mask)

        cv.drawContours(result_frame, good_contours, -1, (0,255,0), 1)

        return result_frame
    
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