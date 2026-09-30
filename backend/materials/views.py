from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Material
from .serializers import MaterialSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def materials_list(request):
    """
    GET /api/materials
    """

    materials = Material.objects.filter(user=request.user)

    serializer = MaterialSerializer(
        materials,
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def material_upload(request):
    """
    POST /api/materials/upload
    """

    serializer = MaterialSerializer(
        data=request.data,
        context={"request": request},
    )

    if not serializer.is_valid():
        return Response(
            {
                "error": "Validation failed.",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    uploaded_file = request.FILES.get("file")

    material = serializer.save(
        user=request.user,
        file_size=uploaded_file.size if uploaded_file else 0,
        material_type=_get_material_type(uploaded_file),
    )

    return Response(
        MaterialSerializer(
            material,
            context={"request": request},
        ).data,
        status=status.HTTP_201_CREATED,
    )


def _get_material_type(uploaded_file):
    if not uploaded_file:
        return "other"

    extension = uploaded_file.name.lower().rsplit(".", 1)[-1]

    if extension == "pdf":
        return "pdf"

    if extension == "ppt":
        return "ppt"

    if extension == "pptx":
        return "pptx"

    if extension in {"mp4", "mov", "avi", "mkv", "webm"}:
        return "video"

    return "other"


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def material_delete(request, material_id):
    material = get_object_or_404(
        Material,
        id=material_id,
        user=request.user,
    )

    material.delete()

    return Response(
        {
            "message": "Material deleted successfully."
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def material_reprocess(request, material_id):
    material = get_object_or_404(
        Material,
        id=material_id,
        user=request.user,
    )

    material.status = "processing"
    material.save(update_fields=["status", "updated_at"])

    return Response(
        MaterialSerializer(
            material,
            context={"request": request},
        ).data,
        status=status.HTTP_200_OK,
    )