from rest_framework import serializers


class PublicHomepageConfigSerializer(serializers.Serializer):
    """
    Serializer for public homepage configuration.
    """

    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(max_length=255)
    welcome_message = serializers.CharField(max_length=255)
    about_us = serializers.CharField()
    hero_image_url = serializers.URLField()


class PublicHomepageConfigUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating public homepage configuration.
    """

    title = serializers.CharField(max_length=255, required=False)
    subtitle = serializers.CharField(max_length=255, required=False)
    welcome_message = serializers.CharField(max_length=255, required=False)
    about_us = serializers.CharField(required=False)
    hero_image = serializers.FileField(required=False)
