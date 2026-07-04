from rest_framework import serializers

class RegulationQueryListSerializer(serializers.Serializer):
    """Serializer for listing regulations with query parameters"""

    season_id = serializers.IntegerField(required=False)