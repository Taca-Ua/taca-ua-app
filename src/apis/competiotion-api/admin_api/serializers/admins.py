"""
Admin user serializers for Keycloak integration
"""

from rest_framework import serializers

from .nucleus import NucleosListSerializer


class AdminListSerializer(serializers.Serializer):
    """Serializer for listing admin users"""

    id = serializers.CharField(read_only=True, help_text="Keycloak user ID")
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    role = serializers.CharField(
        read_only=True,
        help_text="Admin role assigned to the user",
    )
    enabled = serializers.BooleanField(
        read_only=True, help_text="Whether the account is enabled"
    )


class AdminDetailSerializer(AdminListSerializer):
    """Serializer for detailed admin user view"""

    nucleos = NucleosListSerializer(
        many=True,
        help_text="List of nucleus associated with the admin (if applicable)",
    )
    pass


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
    first_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="First name of the admin",
    )
    last_name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Last name of the admin",
    )
    role = serializers.ChoiceField(
        choices=["general_admin", "nucleo_admin"],
        required=True,
        help_text="Role to assign to the admin ('admin_geral' or 'admin_nucleo')",
    )
    nucleos = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=True,
        help_text="List of nucleus IDs to associate with the admin (only for 'admin_nucleo' role)",
    )


class AdminUpdateSerializer(serializers.Serializer):
    """Serializer for updating an admin user"""

    email = serializers.EmailField(
        required=False,
        help_text="New email address",
    )
    first_name = serializers.CharField(
        required=False,
        max_length=255,
        help_text="New first name",
    )
    last_name = serializers.CharField(
        required=False,
        max_length=255,
        help_text="New last name",
    )
    enabled = serializers.BooleanField(
        required=False,
        help_text="Enable or disable the account",
    )
    nucleos = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="Updated list of nucleus IDs to associate with the admin (only for 'admin_nucleo' role)",
    )


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
