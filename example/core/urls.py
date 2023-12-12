from django.urls import path

from .views import IOSerializerDebugView

urlpatterns = [
    path("debug/io-serializer/", IOSerializerDebugView.as_view()),
]
