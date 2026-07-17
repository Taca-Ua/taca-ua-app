from rest_framework import serializers


class ModalityFilterSerializer(serializers.Serializer):
    modality_id = serializers.UUIDField(
        required=False, help_text="ID of the modality to retrieve the ranking for"
    )
