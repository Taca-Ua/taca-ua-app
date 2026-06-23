from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin, require_roles_class_method
from shared.auth.utils import RolesEnum

from ..selectors import get_athlete_by_id, get_athletes_table
from ..service import (
    create_athlete,
    delete_athlete,
    sync_athletes_membership_status,
    update_athlete,
)
from .filters import AthleteListRequestSerializer
from .serializers import (
    AthleteCreateSerializer,
    AthleteDetailSerializer,
    AthleteListSerializer,
    AthleteMembershipSyncSerializer,
    AthleteUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List athletes",
        description="Retrieve a list of athletes with optional filtering by course or team.",
        tags=["Athletes Management"],
        parameters=[AthleteListRequestSerializer],
        responses={200: AthleteListSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create athlete",
        description="Create a new athlete with the provided details.",
        tags=["Athletes Management"],
        request=AthleteCreateSerializer,
        responses={201: AthleteDetailSerializer},
    ),
)
class AthleteListCreateAPIView(RoleRequiredMixin, APIView):
    def get(self, request):
        serializer = AthleteListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        athletes = get_athletes_table(
            course_id=serializer.validated_data.get("course_id"),
            team_id=serializer.validated_data.get("team_id"),
        ).all()

        serializer = AthleteListSerializer(athletes, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = AthleteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        athlete = create_athlete(
            name=serializer.validated_data["name"],
            student_number=serializer.validated_data["student_number"],
            course_id=serializer.validated_data["course_id"],
            course_proof_file=serializer.validated_data.get("course_proof"),
            payment_proof_file=serializer.validated_data.get("payment_proof"),
        )

        serializer = AthleteDetailSerializer(get_athlete_by_id(athlete.id))
        return Response(serializer.data, status=201)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve athlete",
        description="Get detailed information about a specific athlete by ID.",
        tags=["Athletes Management"],
        responses={200: AthleteDetailSerializer},
    ),
    put=extend_schema(
        summary="Update athlete",
        description="Update the details of an existing athlete by ID.",
        tags=["Athletes Management"],
        request=AthleteUpdateSerializer,
        responses={200: AthleteDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete athlete",
        description="Remove an athlete from the system by ID.",
        tags=["Athletes Management"],
        responses={204: None},
    ),
)
class AthleteRetrieveUpdateDeleteAPIView(RoleRequiredMixin, APIView):
    def get(self, request, athlete_id):

        athlete = get_athlete_by_id(athlete_id)

        serializer = AthleteDetailSerializer(athlete)
        return Response(serializer.data, status=200)

    def put(self, request, athlete_id):
        serializer = AthleteUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        athlete = update_athlete(
            athlete_id=athlete_id,
            name=serializer.validated_data.get("name"),
            student_number=serializer.validated_data.get("student_number"),
            course_id=serializer.validated_data.get("course_id"),
            is_member=serializer.validated_data.get("is_member"),
        )

        serializer = AthleteDetailSerializer(get_athlete_by_id(athlete.id))
        return Response(serializer.data, status=200)

    def delete(self, request, athlete_id):
        delete_athlete(athlete_id)
        return Response(status=204)


@extend_schema(
    summary="Sync athlete membership",
    description="Synchronize athlete membership status based on a list of student numbers.",
    tags=["Athletes Management"],
    request=AthleteMembershipSyncSerializer,
    responses={200: None},
)
class AthleteMembershipSyncAPIView(RoleRequiredMixin, APIView):
    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request):
        serializer = AthleteMembershipSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sync_athletes_membership_status(
            athlete_numbers=serializer.validated_data["student_numbers"]
        )

        return Response(status=200)


urlpatterns = [
    path("", AthleteListCreateAPIView.as_view(), name="athlete-list-create"),
    path(
        "<uuid:athlete_id>/",
        AthleteRetrieveUpdateDeleteAPIView.as_view(),
        name="athlete-detail",
    ),
    path(
        "membership-sync/",
        AthleteMembershipSyncAPIView.as_view(),
        name="athlete-membership-sync",
    ),
]
