from rest_framework import serializers


class NucleusSeasonContextSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(required=False, allow_null=True)
