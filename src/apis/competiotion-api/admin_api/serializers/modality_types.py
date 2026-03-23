from rest_framework import serializers


class _EscalaoSerializer(serializers.Serializer):
    """Serializer for Escalao within ModalityType serializers"""

    escalao = serializers.CharField()
    minParticipants = serializers.IntegerField(required=False, allow_null=True)
    maxParticipants = serializers.IntegerField(required=False, allow_null=True)
    points = serializers.ListField(child=serializers.IntegerField())


class ModalityTypeMinimalSerializer(serializers.Serializer):
    """Minimal serializer for modality type"""

    id = serializers.UUIDField()
    name = serializers.CharField()


class ModalityTypeListSerializer(serializers.Serializer):
    """Serializer for listing modality types simply"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    escaloes = _EscalaoSerializer(many=True)
    is_playoff = serializers.BooleanField(default=False)
    tournament_competitor_type = serializers.ChoiceField(
        choices=["individual", "team"], required=False, allow_null=True
    )

    created_at = serializers.DateTimeField(default_timezone=None)


class ModalityTypeDetailSerializer(ModalityTypeListSerializer):
    """Serializer for modality type details"""

    pass


class ModalityTypeCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality type"""

    name = serializers.CharField()
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    escaloes = _EscalaoSerializer(many=True)
    is_playoff = serializers.BooleanField(default=False)
    tournament_competitor_type = serializers.ChoiceField(
        choices=["individual", "team"], required=False, allow_null=True
    )


class ModalityTypeUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality type"""

    name = serializers.CharField(required=False)
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    escaloes = _EscalaoSerializer(many=True, required=False)
    is_playoff = serializers.BooleanField(required=False)
    tournament_competitor_type = serializers.ChoiceField(
        choices=["individual", "team"], required=False, allow_null=True
    )
