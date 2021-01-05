from django.urls import path
from . import views

urlpatterns = [
    path("", views.live, name="live"),
    path("stream.mjpg", views.camera_image_stream, name="stream.mjpg")
]