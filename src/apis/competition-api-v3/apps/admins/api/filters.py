from rest_framework import serializers


class AdminListFilter(serializers.Serializer):
    """Serializer for filtering admin users in the list endpoint."""

    include_inactive = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Include inactive admin users in the list (default: false)",
    )
