from rest_framework import serializers


class _EscalaoSerializer(serializers.Serializer):
    """Serializer for Escalao within ModalityType serializers"""

    escalao = serializers.CharField()
    minParticipants = serializers.IntegerField()
    maxParticipants = serializers.IntegerField()
    points = serializers.ListField(child=serializers.IntegerField())


class ModalityTypeListSerializer(serializers.Serializer):
    """Serializer for listing modality types"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    escaloes = _EscalaoSerializer(many=True)


class ModalityTypeCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality type"""

    name = serializers.CharField()
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    escaloes = _EscalaoSerializer(many=True)

    created_by = serializers.UUIDField(required=False)
    created_at = serializers.DateTimeField(required=False, default_timezone=None)
    updated_at = serializers.DateTimeField(required=False, default_timezone=None)


class ModalityTypeUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality type"""

    name = serializers.CharField(required=False)
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    escaloes = _EscalaoSerializer(many=True, required=False)


class ModalityTypeDetailSerializer(serializers.Serializer):
    """Serializer for modality type details"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    escaloes = _EscalaoSerializer(many=True)

    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField(default_timezone=None)
    updated_at = serializers.DateTimeField(default_timezone=None)
