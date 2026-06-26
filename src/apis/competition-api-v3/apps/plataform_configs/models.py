from typing import TYPE_CHECKING

from django.db import models


class PublicWebsiteHomePage(models.Model):
    """
    Model representing the home page configuration for the public website.
    """

    _bucket = models.IntegerField(1)

    title = models.CharField(max_length=255, help_text="Title of the home page")
    subtitle = models.CharField(max_length=255, help_text="Subtitle of the home page")
    welcome_message = models.CharField(
        max_length=255, help_text="Welcome message for the home page"
    )
    about_us = models.TextField(help_text="About us section for the home page")
    hero_image_url = models.URLField(
        help_text="URL of the hero image for the home page"
    )

    if TYPE_CHECKING:
        sponsors: models.QuerySet["Sponsor"]

    class Meta:
        unique_together = (
            "_bucket",
        )  # Ensures that there is only one home page configuration in the database

    def __str__(self):
        return f"PublicWebsiteHomePage (Bucket: {self._bucket})"


class Sponsor(models.Model):
    """
    Model representing a sponsor for the public website.
    """

    conf = models.ForeignKey(
        PublicWebsiteHomePage, on_delete=models.CASCADE, related_name="sponsors"
    )
    name = models.CharField(max_length=255, help_text="Name of the sponsor")
    logo_url = models.URLField(help_text="URL of the sponsor's logo")
    website_url = models.URLField(help_text="URL of the sponsor's website")

    class Meta:
        unique_together = (
            "conf",
            "name",
        )

    def __str__(self):
        return f"Sponsor: {self.name} (Home Page: {self.conf.title})"
