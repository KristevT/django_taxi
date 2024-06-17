"""Module for configuring Aggregator, TaxiDriver and Order models in the admin panel."""

from django.contrib import admin

from taxi_app.models import Aggregator, Order, TaxiDriver, TaxiDriverAggregator

ID = 'id'


@admin.register(Aggregator)
class AggregatorAdmin(admin.ModelAdmin):
    """Aggregator admin configuration."""

    list_display = (
        ID,
        'name',
        'phone',
    )
    readonly_fields = (ID,)


@admin.register(TaxiDriver)
class TaxiDriverAdmin(admin.ModelAdmin):
    """Taxi Driver admin configuration."""

    list_display = (
        ID,
        'first_name',
        'last_name',
        'phone_number',
        'car',
    )
    readonly_fields = ('id',)


@admin.register(TaxiDriverAggregator)
class TaxiDriverAggregatorAdmin(admin.ModelAdmin):
    """Taxi Driver to Aggregator relationship admin configuration."""

    list_display = (
        ID,
        'taxi_driver',
        'aggregator',
    )
    readonly_fields = (ID,)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin configuration."""

    list_display = (
        ID,
        'name',
        'date',
        'cost',
        'pickup_address',
        'destination_address',
        'taxi_driver',
    )
    readonly_fields = (ID,)
