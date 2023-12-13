from django.urls import path

from .views import ImprovedJSONRendererView, IOSerializerDebugView

urlpatterns = [
    path("debug/io-serializer/", IOSerializerDebugView.as_view()),
    path(
        "improved-json-renderer/",
        ImprovedJSONRendererView.as_view(),
        name="improved-json-renderer",
    ),
]
