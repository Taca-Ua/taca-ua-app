from rest_framework import serializers


# Response serializers
class SponsorSerializer(serializers.Serializer):
    """
    Serializer for sponsor information.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    logo_url = serializers.URLField()
    website_url = serializers.URLField()


class PublicHomepageConfigSerializer(serializers.Serializer):
    """
    Serializer for public homepage configuration.
    """

    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(max_length=255)
    welcome_message = serializers.CharField(max_length=255)
    about_us = serializers.CharField()
    hero_image_url = serializers.URLField()
    sponsors = SponsorSerializer(many=True)


# Request serializers
class PublicHomepageConfigUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating public homepage configuration.
    """

    title = serializers.CharField(max_length=255, required=False)
    subtitle = serializers.CharField(max_length=255, required=False)
    welcome_message = serializers.CharField(max_length=255, required=False)
    about_us = serializers.CharField(required=False)
    hero_image = serializers.FileField(required=False)


class SponsorCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new sponsor.
    """

    name = serializers.CharField(max_length=255)
    logo = serializers.FileField()
    website_url = serializers.URLField()
