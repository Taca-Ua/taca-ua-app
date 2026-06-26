from apps.plataform_configs.models import PublicWebsiteHomePage, Sponsor
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


@receiver(post_save, sender=PublicWebsiteHomePage)
def update_home_page_config(sender, instance, **kwargs):
    request_projection_update(
        ProjectionUpdateRequestTypes.HOME_PAGE_CONFIG, {}, key="home_page_config"
    )


@receiver(post_save, sender=Sponsor)
def update_sponsor(sender, instance, **kwargs):
    request_projection_update(
        ProjectionUpdateRequestTypes.HOME_PAGE_CONFIG, {}, key="home_page_config"
    )


@receiver(post_delete, sender=Sponsor)
def delete_sponsor(sender, instance, **kwargs):
    request_projection_update(
        ProjectionUpdateRequestTypes.HOME_PAGE_CONFIG, {}, key="home_page_config"
    )
