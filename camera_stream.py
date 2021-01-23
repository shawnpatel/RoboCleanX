import cv2 as cv

class CameraStream():
    def __init__(self):
        self.camera = cv.VideoCapture(0)
        
        self.camera.set(cv.CAP_PROP_FRAME_WIDTH, 640) # Width
        self.camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480) # Height
        self.camera.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M','J','P','G'))
        self.camera.set(cv.CAP_PROP_FPS, 15) # FPS

        self.camera.set(cv.CAP_PROP_BRIGHTNESS, 1) # Brightness
        self.camera.set(cv.CAP_PROP_CONTRAST, 0.5) # Contrast
        #self.camera.set(cv.CAP_PROP_SATURATION, 0.75) # Saturation
        #self.camera.set(cv.CAP_PROP_HUE, 1) # Hue
        #self.camera.set(cv.CAP_PROP_GAIN, 1) # Gain
        #self.camera.set(cv.CAP_PROP_EXPOSURE, 0.5) # Exposure
    
    def frame_generator(self):
        while True:
            success, frame = self.camera.read()

            if not success:
                print("Unable to get frame from camera.")
                self.terminate()
                break
            else:
                ret, buffer = cv.imencode(".jpg", frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' +
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def terminate(self):
        self.camera.release()