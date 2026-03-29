"""
Match management serializers
"""

from rest_framework import serializers

class NucleosListSerializer(serializers.Serializer):
    """
    Serializer para listagem de núcleos. 
    Usado para devolver dados ao Frontend.
    """
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    abbreviation = serializers.CharField()
    # Este campo contém o link final da imagem (ex: do MinIO ou S3)
    logo_url = serializers.CharField(required=False, allow_null=True)


class NucleosDetailSerializer(NucleosListSerializer):
    """
    Serializer para detalhes de um núcleo específico.
    Herda de NucleosListSerializer para manter a consistência.
    """
    pass


class NucleosCreateSerializer(serializers.Serializer):
    """
    Serializer para a criação de um novo núcleo.
    Suporta o envio de um ficheiro de imagem real.
    """
    name = serializers.CharField(required=True)
    abbreviation = serializers.CharField(required=True)
    # Campo para receber o ficheiro binário via multipart/form-data
    logo = serializers.ImageField(required=False, write_only=True)


class NucleosUpdateSerializer(serializers.Serializer):
    """
    Serializer para a atualização de núcleos existentes.
    Todos os campos são opcionais para permitir atualizações parciais (PATCH-like).
    """
    name = serializers.CharField(required=False)
    abbreviation = serializers.CharField(required=False)
    # Campo para substituir o logo atual por um novo ficheiro
    logo = serializers.ImageField(required=False, write_only=True)