"""Module for configuring this Taxi Application."""

from django.apps import AppConfig


class TaxiAppConfig(AppConfig):
    """Taxi Application Configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taxi_app'
