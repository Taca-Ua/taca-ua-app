from rest_framework import serializers


class ModalityTypeFilterSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(
        required=False, help_text="Filter modality types by season ID."
    )
    mode = serializers.ChoiceField(
        choices=["modality", "points"],
        required=False,
        help_text="Filter modality types by mode.",
    )
