from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from .stream import Stream
from threading import Thread

# Create your views here.
def live(request):
    return render(request, "camera_stream/live.html")

def camera_image_stream(request):
    stream = Stream()

    recording_thread = Thread(target=stream.start_recording)
    recording_thread.start()

    return StreamingHttpResponse(stream.frame_generator(), content_type="multipart/x-mixed-replace;boundary=frame")