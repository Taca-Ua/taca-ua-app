from rest_framework import serializers


class RankingSeasonFilterSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(
        required=True, help_text="ID of the season to retrieve the ranking for"
    )
