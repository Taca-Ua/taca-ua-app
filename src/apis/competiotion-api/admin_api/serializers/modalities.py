from rest_framework import serializers

from .modality_types import ModalityTypeListSerializer, ModalityTypeMinimalSerializer


class ModalityListSerializer(serializers.Serializer):
    """Serializer for listing modalities"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    modality_type = ModalityTypeMinimalSerializer()


class ModalityDetailSerializer(ModalityListSerializer):
    """Serializer for modality details"""

    modality_type = ModalityTypeListSerializer()


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    modality_type_id = serializers.UUIDField(required=False)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    modality_type_id = serializers.UUIDField(required=False)
