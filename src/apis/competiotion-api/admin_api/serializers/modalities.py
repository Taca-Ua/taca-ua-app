"""
Modality management serializers
"""

from rest_framework import serializers

MODALITY_TYPES = [
    "coletiva recorrente",
    "coletiva pontual",
    "individual",
    "pares",
    "individual/pares",
]


class ModalityListSerializer(serializers.Serializer):
    """Serializer for listing modalities"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    modality_type = serializers.CharField()


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    modality_type_id = serializers.UUIDField(required=False)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    modality_type_id = serializers.UUIDField(required=False)
