from flask import Flask, Response, render_template
import socket
from camera_stream import CameraStream

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    camera_stream = CameraStream()
    camera_stream.start()

    return Response(camera_stream.frame_generator(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/terminate")
def terminate():
    return "Terminated."

def main():
    host = "{}.lan".format(socket.gethostname())
    port = 8000
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    main()