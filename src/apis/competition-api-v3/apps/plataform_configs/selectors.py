from .models import PublicWebsiteHomePage


def get_home_page_config():
    """
    Retrieve the home page configuration for the public website.

    Returns:
        PublicWebsiteHomePage: The home page configuration instance.
    """
    return PublicWebsiteHomePage.objects.get(_bucket=1)
