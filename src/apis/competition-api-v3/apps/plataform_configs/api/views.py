from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin, require_roles_class_method
from shared.auth.utils import RolesEnum

from ..selectors import get_home_page_config
from ..service import update_home_page_config
from .serializers import (
    PublicHomepageConfigSerializer,
    PublicHomepageConfigUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        description="Get the public homepage configuration",
        responses={
            status.HTTP_200_OK: PublicHomepageConfigSerializer,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["Public Homepage Config"],
    ),
    put=extend_schema(
        description="Update the public homepage configuration",
        request=PublicHomepageConfigUpdateSerializer,
        responses={
            status.HTTP_200_OK: PublicHomepageConfigSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["Public Homepage Config"],
    ),
)
class PublicHomepageConfigView(RoleRequiredMixin, APIView):

    def get(self, request: Request) -> Response:
        """
        Get the public homepage configuration.
        """
        config_data = get_home_page_config()

        serializer = PublicHomepageConfigSerializer(config_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request: Request) -> Response:
        """
        Update the public homepage configuration.
        """
        serializer = PublicHomepageConfigUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_home_page_config(serializer.validated_data)

        serializer = PublicHomepageConfigSerializer(get_home_page_config())
        return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path(
        "public-homepage-config/",
        PublicHomepageConfigView.as_view(),
        name="public-homepage-config",
    ),
]
