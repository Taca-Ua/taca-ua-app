from ..base import BaseFormat


class FreeFormat(BaseFormat):

    def create(self, format_data: dict):
        # No specific settings for free format, so we just return an empty details
        return self.get_details()

    def update(self, format_data: dict):
        # No specific settings to update for free format, so we just return the current details
        return self.get_details()

    def get_details(self) -> dict:
        # Free format has no specific settings, so we return an empty dictionary
        return {}

    def record_result(self, match) -> dict:
        # Free format does not have specific result recording logic, so we just return an empty details
        return {}

    def suggest_matches(self, *args, **kwargs):
        raise ValueError("Free format does not support match suggestions.")

    def generate_matches(self, *args, **kwargs):
        raise ValueError("Free format does not support match generation.")
