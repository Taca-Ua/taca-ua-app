from rest_framework import serializers

# from ..tournaments.serializers import TournamentSerializer


class MatchListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    # tournament = TournamentSerializer()


class MatchCreateSerializer(serializers.Serializer):
    tournament_id = serializers.UUIDField()


class MatchUpdateSerializer(serializers.Serializer):
    tournament_id = serializers.UUIDField(required=False)
