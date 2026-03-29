"""
Modality management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.parsers import MultiPartParser, FormParser
from ..services.file_service import FileService

from ..decorators import RoleRequiredMixin
from ..serializers.nucleus import (
    NucleosCreateSerializer,
    NucleosDetailSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


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
        nucleos = modalities_service_client.list_nucleos()

        # Serialize output data
        serializer = NucleosListSerializer(nucleos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        # Serialize input data
        serializer = NucleosCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logo_url = None
        if 'logo' in request.FILES:
            # Faz upload para o MinIO/S3 e retorna a URL pública
            upload_res = self.file_service.upload_file(request.FILES['logo'], file_type="image")
            logo_url = upload_res["file_url"]

        nucleo = modalities_service_client.create_nucleo(
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
        nucleo = modalities_service_client.get_nucleo(nucleo_id)
        serializer = NucleosDetailSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, nucleo_id):
        # 1. Validar os dados de texto (nome, abreviatura)
        serializer = NucleosUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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
            nucleo_id,
            name=serializer.validated_data.get("name"),
            abbreviation=serializer.validated_data.get("abbreviation"),
            logo_url=logo_url  # Enviamos a nova URL ou a antiga preservada
        )

        # 5. Retornar os dados atualizados
        serializer = NucleosDetailSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, nucleo_id):
        modalities_service_client.delete_nucleo(nucleo_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

urlpatterns = [
    path("", NucleoListCreateView.as_view(), name="nucleo-list"),
    path("<uuid:nucleo_id>/", NucleoDetailView.as_view(), name="nucleo-detail"),
]
