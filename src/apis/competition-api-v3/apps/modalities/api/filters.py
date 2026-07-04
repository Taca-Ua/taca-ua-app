from rest_framework import serializers


class ModalityQuerySerializer(serializers.Serializer):
    season_id = serializers.IntegerField(required=False)
