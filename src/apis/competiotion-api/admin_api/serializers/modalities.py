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
    type = serializers.ChoiceField(choices=MODALITY_TYPES)
    scoring_schema = serializers.JSONField(required=False, allow_null=True)


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=MODALITY_TYPES, required=True)
    scoring_schema = serializers.JSONField(required=False, allow_null=True)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=MODALITY_TYPES, required=False)
    scoring_schema = serializers.JSONField(required=False, allow_null=True)
