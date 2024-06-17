"""Module defining serializers for the application."""

from rest_framework import serializers

from taxi_app.models import Aggregator, Order, TaxiDriver, TaxiDriverAggregator

FIELDS_ALL = '__all__'
USERNAME = 'user.username'


class AggregatorSerializer(serializers.ModelSerializer):
    """Serializer class for Aggregator model."""

    user = serializers.ReadOnlyField(source=USERNAME)

    class Meta:
        model = Aggregator
        fields = FIELDS_ALL


class TaxiDriverSerializer(serializers.ModelSerializer):
    """Serializer class for Taxi Driver model."""

    user = serializers.ReadOnlyField(source=USERNAME)

    class Meta:
        model = TaxiDriver
        fields = FIELDS_ALL


class TaxiDriverAggregatorSerializer(serializers.ModelSerializer):
    """Serializer class for Taxi Driver to Aggregator relationship model."""

    user = serializers.ReadOnlyField(source=USERNAME)

    class Meta:
        model = TaxiDriverAggregator
        fields = FIELDS_ALL


class OrderSerializer(serializers.ModelSerializer):
    """Serializer class for Order model."""

    user = serializers.ReadOnlyField(source=USERNAME)

    class Meta:
        model = Order
        fields = FIELDS_ALL
