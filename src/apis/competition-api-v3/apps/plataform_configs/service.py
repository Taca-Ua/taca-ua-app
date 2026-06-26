from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from shared.file_storage.minio_service import MinioService

from .models import PublicWebsiteHomePage

# init the MinioService for handling file storage related to regulations
file_storage_service = MinioService("public-website-homepage")


@transaction.atomic
def create_initial_config():
    """
    Create the initial home page configuration for the public website.
    This function creates a default configuration with predefined values.
    Should be called only once during the initial setup of the application by the bootstrap_public_homepage_config management command.
    """

    # Check if the home page configuration already exists
    if not PublicWebsiteHomePage.objects.filter(_bucket=1).exists():
        # Create a new home page configuration with default values
        PublicWebsiteHomePage.objects.create(
            _bucket=1,
            title="Welcome to Our Platform",
            subtitle="Your gateway to innovation",
            welcome_message="We are thrilled to have you here! Explore our platform and discover the endless possibilities.",
            about_us="Our platform is dedicated to fostering innovation and collaboration. Join us on this exciting journey!",
            hero_image_url="",
        )


@transaction.atomic
def update_home_page_config(
    title: str = None,
    subtitle: str = None,
    welcome_message: str = None,
    about_us: str = None,
    hero_image: UploadedFile = None,
):
    """
    Update the home page configuration for the public website.

    Args:
        bucket (int): The bucket identifier for the home page configuration.
        title (str): The title of the home page.
        subtitle (str): The subtitle of the home page.
        welcome_message (str): The welcome message for the home page.
        about_us (str): The about us section for the home page.
        hero_image_url (str): The URL of the hero image for the home page.
    """

    # Retrieve the existing home page configuration or create a new one if it doesn't exist
    home_page_config = PublicWebsiteHomePage.objects.get(_bucket=1)

    # Update the fields with the provided values
    if title is not None:
        home_page_config.title = title
    if subtitle is not None:
        home_page_config.subtitle = subtitle
    if welcome_message is not None:
        home_page_config.welcome_message = welcome_message
    if about_us is not None:
        home_page_config.about_us = about_us
    if hero_image is not None:
        if home_page_config.hero_image_url:
            # Delete the existing hero image from Minio if it exists
            file_storage_service.delete_file(home_page_config.hero_image_url)
        hero_image_url = file_storage_service.upload_file(
            hero_image, f"hero_image_{hero_image.name}"
        )
        home_page_config.hero_image_url = hero_image_url

    # Save the updated configuration to the database
    home_page_config.save()
