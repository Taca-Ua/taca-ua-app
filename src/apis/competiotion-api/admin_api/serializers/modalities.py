from rest_framework import serializers


class ModalityListSerializer(serializers.Serializer):
    """Serializer for listing modalities"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    modality_type_name = serializers.CharField()


class ModalityDetailSerializer(serializers.Serializer):
    """Serializer for modality details"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    modality_type_id = serializers.UUIDField()
    modality_type_name = serializers.CharField()


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    modality_type_id = serializers.UUIDField(required=False)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    modality_type_id = serializers.UUIDField(required=False)
