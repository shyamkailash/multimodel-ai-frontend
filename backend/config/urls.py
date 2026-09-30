from django.contrib import admin
from django.urls import path

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def api_root(request):
    return Response({
        "name": "AI Personalized Learning Companion API",
        "version": "1.0",
        "status": "running",
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
]