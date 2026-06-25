from django.db import transaction

from .models import PublicWebsiteHomePage


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
            hero_image_url="https://example.com/default-hero-image.jpg",
        )


@transaction.atomic
def update_home_page_config(
    title: str, subtitle: str, welcome_message: str, about_us: str, hero_image_url: str
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
    home_page_config = PublicWebsiteHomePage.objects.get(bucket=1)

    # Update the fields with the provided values
    home_page_config.title = title
    home_page_config.subtitle = subtitle
    home_page_config.welcome_message = welcome_message
    home_page_config.about_us = about_us
    home_page_config.hero_image_url = hero_image_url

    # Save the updated configuration to the database
    home_page_config.save()
