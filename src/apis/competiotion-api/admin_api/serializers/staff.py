"""
Staff serializers
"""

from rest_framework import serializers


class StaffListSerializer(serializers.Serializer):
    """Serializer for listing staff"""

    id = serializers.UUIDField()
    full_name = serializers.CharField()
    staff_number = serializers.CharField(required=False, allow_null=True)
    contact = serializers.CharField(required=False, allow_null=True)


class StaffDetailSerializer(StaffListSerializer):
    """Serializer for detailed staff view"""

    pass


class StaffCreateSerializer(serializers.Serializer):
    """Serializer for creating a staff member"""

    full_name = serializers.CharField(required=True)
    staff_number = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)

    def validate(self, data):
        """Ensure at least one of staff_number or contact is provided"""
        if not data.get("staff_number") and not data.get("contact"):
            raise serializers.ValidationError(
                "Either staff_number or contact must be provided."
            )
        return data


class StaffUpdateSerializer(serializers.Serializer):
    """Serializer for updating a staff member"""

    full_name = serializers.CharField(required=False)
    staff_number = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)
