"""
Staff serializers
"""

from rest_framework import serializers


class StaffListSerializer(serializers.Serializer):
    """Serializer for listing staff"""

    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField()
    staff_number = serializers.CharField()
    contact = serializers.CharField()


class StaffCreateSerializer(serializers.Serializer):
    """Serializer for creating a staff member"""

    full_name = serializers.CharField(required=True)
    staff_number = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)


class StaffUpdateSerializer(serializers.Serializer):
    """Serializer for updating a staff member"""

    full_name = serializers.CharField(required=False)
    staff_number = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)
