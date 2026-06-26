from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import (
    RoleRequiredMixin,
    require_roles,
    require_roles_class_method,
)
from shared.auth.utils import RolesEnum

from ..selectors import get_home_page_config
from ..service import create_sponsor, remove_sponsor, update_home_page_config
from .serializers import (
    PublicHomepageConfigSerializer,
    PublicHomepageConfigUpdateSerializer,
    SponsorCreateSerializer,
    SponsorSerializer,
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

        update_home_page_config(
            title=serializer.validated_data.get("title"),
            subtitle=serializer.validated_data.get("subtitle"),
            welcome_message=serializer.validated_data.get("welcome_message"),
            about_us=serializer.validated_data.get("about_us"),
            hero_image=serializer.validated_data.get("hero_image"),
        )

        serializer = PublicHomepageConfigSerializer(get_home_page_config())
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Add a new sponsor to the public homepage configuration",
    request=SponsorCreateSerializer,
    responses={
        status.HTTP_201_CREATED: SponsorSerializer,
        status.HTTP_400_BAD_REQUEST: None,
        status.HTTP_403_FORBIDDEN: None,
    },
)
@api_view(["POST"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def add_sponsor_view(request: Request) -> Response:
    """
    Add a new sponsor to the public homepage configuration.
    """
    serializer = SponsorCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    new_sponsor = create_sponsor(
        name=serializer.validated_data["name"],
        website_url=serializer.validated_data["website_url"],
        logo=serializer.validated_data["logo"],
    )

    serializer = SponsorSerializer(new_sponsor)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    description="Remove a sponsor from the public homepage configuration",
    responses={
        status.HTTP_204_NO_CONTENT: None,
        status.HTTP_403_FORBIDDEN: None,
        status.HTTP_404_NOT_FOUND: None,
    },
)
@api_view(["DELETE"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def remove_sponsor_view(request: Request, sponsor_id: int) -> Response:
    """
    Remove a sponsor from the public homepage configuration.
    """

    remove_sponsor(sponsor_id=sponsor_id)

    serializer = PublicHomepageConfigSerializer(get_home_page_config())
    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path(
        "public-homepage-config/",
        PublicHomepageConfigView.as_view(),
        name="public-homepage-config",
    ),
    path(
        "public-homepage-config/sponsors/",
        add_sponsor_view,
        name="add-sponsor",
    ),
    path(
        "public-homepage-config/sponsors/<int:sponsor_id>/",
        remove_sponsor_view,
        name="remove-sponsor",
    ),
]
