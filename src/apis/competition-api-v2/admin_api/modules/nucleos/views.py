"""
Nucleo management views
"""

from admin_api.utils.decorators import RoleRequiredMixin, require_roles_class_method
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

<<<<<<< HEAD:src/apis/competition-api-v2/admin_api/modules/nucleos/views.py
from .serializers import (
    FileService,
    FormParser,
    MultiPartParser,
    NucleosCreateSerializer,
    NucleosDetailSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
    RoleRequiredMixin,
    02edffb2045a79c2f37d752e668240a5161cf0dd:src/apis/competiotion-api/admin_api/views/nucleus.py,
    ..decorators,
    ..serializers.nucleus,
    ..services.file_service,
    =======,
    >>>>>>>,
    from,
    import,
    rest_framework.parsers,
)
from .service import nucleos_service


@extend_schema_view(
    get=extend_schema(
        responses=NucleosListSerializer(many=True),
        description="List all nucleos",
        tags=["Nucleo Management"],
    ),
    post=extend_schema(
        request=NucleosCreateSerializer,
        responses=NucleosListSerializer,
        description="Create a new nucleo",
        tags=["Nucleo Management"],
    ),
)
class NucleoListCreateView(RoleRequiredMixin, APIView):
    parser_classes = [MultiPartParser, FormParser]
    file_service = FileService()


    def get(self, request: Request):
        nucleos = nucleos_service.list_nucleos(
            admin_id=request.user_id if "nucleo_admin" in request.roles else None
        )

        # Serialize output data
        serializer = NucleosListSerializer(nucleos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def post(self, request: Request):
        # Serialize input data
        serializer = NucleosCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

<<<<<<< HEAD:src/apis/competition-api-v2/admin_api/modules/nucleos/views.py
        nucleo = nucleos_service.create_nucleo(
=======
        logo_url = None
        if 'logo' in request.FILES:
            # Faz upload para o MinIO/S3 e retorna a URL pública
            upload_res = self.file_service.upload_file(request.FILES['logo'], file_type="image")
            logo_url = upload_res["file_url"]

        nucleo = modalities_service_client.create_nucleo(
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd:src/apis/competiotion-api/admin_api/views/nucleus.py
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
            logo_url=logo_url
        )

        # Serialize output data
        serializer = NucleosListSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=NucleosDetailSerializer,
        description="Get a nucleo by ID",
        tags=["Nucleo Management"],
    ),
    put=extend_schema(
        request=NucleosUpdateSerializer,
        responses=NucleosDetailSerializer,
        description="Update a nucleo",
        tags=["Nucleo Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a nucleo",
        tags=["Nucleo Management"],
    ),
)
class NucleoDetailView(RoleRequiredMixin, APIView):
    """
    View para detalhes, atualização e eliminação de núcleos académicos.
    """
    # Necessário para processar FormData e ficheiros binários (imagens)
    parser_classes = [MultiPartParser, FormParser]
    file_service = FileService()

    def get(self, request, nucleo_id):
<<<<<<< HEAD:src/apis/competition-api-v2/admin_api/modules/nucleos/views.py
        nucleo = nucleos_service.get_nucleo(nucleo_id)

        # Serialize output data
=======
        nucleo = modalities_service_client.get_nucleo(nucleo_id)
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd:src/apis/competiotion-api/admin_api/views/nucleus.py
        serializer = NucleosDetailSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def put(self, request, nucleo_id):
        # 1. Validar os dados de texto (nome, abreviatura)
        serializer = NucleosUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

<<<<<<< HEAD:src/apis/competition-api-v2/admin_api/modules/nucleos/views.py
        nucleo = nucleos_service.update_nucleo(
=======
        # 2. Obter o estado atual do núcleo no microserviço core
        # Precisamos disto para saber qual é a logo_url atual caso o utilizador não envie uma nova
        current_nucleo = modalities_service_client.get_nucleo(nucleo_id)

        # Tentamos obter a logo_url atual (seja de um objeto ou dicionário)
        logo_url = getattr(current_nucleo, 'logo_url', None)
        if logo_url is None and isinstance(current_nucleo, dict):
            logo_url = current_nucleo.get('logo_url')

        # 3. Lógica de Upload: Se houver um novo ficheiro no campo 'logo'
        if 'logo' in request.FILES:
            # Upload para o serviço de ficheiros (MinIO/S3)
            upload_res = self.file_service.upload_file(
                request.FILES['logo'],
                file_type="image"
            )
            logo_url = upload_res["file_url"]

        # 4. Enviar a atualização para o microserviço modalities-service
        nucleo = modalities_service_client.update_nucleo(
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd:src/apis/competiotion-api/admin_api/views/nucleus.py
            nucleo_id,
            name=serializer.validated_data.get("name"),
            abbreviation=serializer.validated_data.get("abbreviation"),
            logo_url=logo_url  # Enviamos a nova URL ou a antiga preservada
        )

        # 5. Retornar os dados atualizados
        serializer = NucleosDetailSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def delete(self, request, nucleo_id):
        nucleos_service.delete_nucleo(nucleo_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

urlpatterns = [
    path("", NucleoListCreateView.as_view(), name="nucleo-list"),
    path("<uuid:nucleo_id>/", NucleoDetailView.as_view(), name="nucleo-detail"),
]
