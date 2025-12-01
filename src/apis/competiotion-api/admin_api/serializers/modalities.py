"""
Modality management serializers
"""

from rest_framework import serializers


class ModalityListSerializer(serializers.Serializer):
    """Serializer for listing modalities"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    type = serializers.ChoiceField(choices=["coletiva", "individual", "mista"])
    scoring_schema = serializers.JSONField(required=False, allow_null=True)


class ModalityCreateSerializer(serializers.Serializer):
    """Serializer for creating a modality"""

    name = serializers.CharField(required=True)
    type = serializers.ChoiceField(
        choices=["coletiva", "individual", "mista"], required=True
    )
    scoring_schema = serializers.JSONField(required=False, allow_null=True)


class ModalityUpdateSerializer(serializers.Serializer):
    """Serializer for updating a modality"""

    name = serializers.CharField(required=False)
    type = serializers.ChoiceField(
        choices=["coletiva", "individual", "mista"], required=False
    )
    scoring_schema = serializers.JSONField(required=False, allow_null=True)
