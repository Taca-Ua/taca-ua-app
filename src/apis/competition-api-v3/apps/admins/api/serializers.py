from rest_framework import serializers

from ..models import AdminRole


# Response serializers
class AdminListSerializer(serializers.Serializer):
    """Serializer for listing admin users"""

    id = serializers.CharField(read_only=True, help_text="Keycloak user ID")
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True, help_text="Full name of the admin")
    role = serializers.CharField(
        read_only=True,
        help_text="Admin role assigned to the user",
    )
    enabled = serializers.BooleanField(
        read_only=True, help_text="Whether the account is enabled", source="active"
    )


class AdminDetailSerializer(AdminListSerializer):
    """Serializer for detailed admin user view"""

    class _AdminNucleoSummarySerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        abbreviation = serializers.CharField(read_only=True)

    class _AdminCourseSummarySerializer(serializers.Serializer):
        id = serializers.UUIDField(read_only=True)
        name = serializers.CharField(read_only=True)
        abbreviation = serializers.CharField(read_only=True)

    nucleos = _AdminNucleoSummarySerializer(many=True, required=False)
    courses = _AdminCourseSummarySerializer(many=True, required=False)


# Request serializers
class AdminCreateSerializer(serializers.Serializer):
    """Serializer for creating a new admin user"""

    username = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Unique username for the admin",
    )
    email = serializers.EmailField(
        required=True,
        help_text="Email address for the admin",
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        help_text="Password for the admin account (minimum 8 characters)",
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Full name of the admin",
    )
    role = serializers.ChoiceField(
        choices=AdminRole.values,
        required=True,
        help_text="Role to assign to the admin ('general_admin' or 'nucleo_admin')",
    )
    nucleos = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="List of nucleus IDs to associate with the admin (only for 'nucleo_admin' role)",
    )

    def validate(self, data):
        if data["role"] == AdminRole.GENERAL_ADMIN and data.get("nucleos"):
            raise serializers.ValidationError(
                "Nucleus cannot be associated with a 'general_admin' role"
            )

        return data


class AdminUpdateSerializer(serializers.Serializer):
    """Serializer for updating an admin user"""

    email = serializers.EmailField(
        required=False,
        help_text="New email address",
    )
    name = serializers.CharField(
        required=False,
        max_length=255,
        help_text="New full name",
    )
    enabled = serializers.BooleanField(
        required=False,
        help_text="Enable or disable the account",
    )
    nucleos = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="Updated list of nucleus IDs to associate with the admin (only for 'admin_nucleo' role)",
    )

    def validate(self, data):
        if (data.get("first_name"), data.get("last_name")).count(None) == 1:
            raise serializers.ValidationError(
                "Both first_name and last_name must be provided together for name update."
            )
        return data


class AdminPasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing an admin user's password"""

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        help_text="New password (minimum 8 characters)",
    )
    temporary = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether the password is temporary (user must change on next login)",
    )
