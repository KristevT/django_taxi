"""This module defines data models of this Django application."""

from datetime import datetime, timezone
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def get_datetime() -> datetime:
    """
    Return current date and time.

    Returns:
        datetime: Current date and time
    """
    return datetime.now(timezone.utc)


def validate_future_date(t_value: datetime) -> None:
    """
    Ensure object is not created in the future.

    Args:
        t_value (datetime): Date and time to be validated.

    Raises:
        ValidationError: If date appears to be in the future.
    """
    if t_value > get_datetime():
        raise ValidationError('Не может быть создано в будущем')


def check_positive(number: int | float) -> None:
    """
    Ensure number is not negative.

    Args:
        number (int | float): The value to validate.

    Raises:
        ValidationError: If number appears to be negative.
    """
    if number < 0:
        raise ValidationError(
            'Число не может быть отрицательным',
        )


class UUIDMixin(models.Model):
    """A Mixin class that adds UUID to the object by default."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    """A Mixin class that adds creation date to the object by default."""

    created = models.DateTimeField(auto_now_add=True, validators=[validate_future_date])

    class Meta:
        abstract = True


class UserMixin(models.Model):
    """A Mixin class that marks who created the object."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user')

    class Meta:
        abstract = True


NAME_LENGTH_MAX = 50
TITLE_LENGTH_MAX = 100
PHONE_LENGTH_MAX = 15
ADDRESS_LENGTH_MAX = 250


class Aggregator(UUIDMixin, CreatedMixin, UserMixin):
    """Model representing an Aggregator."""

    name = models.TextField(null=False, blank=False, unique=True, max_length=TITLE_LENGTH_MAX)
    phone = models.TextField(null=False, blank=False, unique=True, max_length=PHONE_LENGTH_MAX)

    taxi_drivers = models.ManyToManyField('TaxiDriver', through='TaxiDriverAggregator')

    def __str__(self):
        """
        Return the title of the aggregator.

        Returns:
            self.name: Aggregator's title as a string
        """
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Aggregator'
        verbose_name_plural = 'Aggregators'


class TaxiDriver(UUIDMixin, UserMixin):
    """Model representing a Taxi Driver."""

    first_name = models.TextField(null=False, blank=False, max_length=NAME_LENGTH_MAX)
    last_name = models.TextField(null=False, blank=False, max_length=NAME_LENGTH_MAX)
    phone_number = models.TextField(null=True, blank=True, max_length=PHONE_LENGTH_MAX)
    car = models.TextField(null=True, blank=True, max_length=TITLE_LENGTH_MAX)

    aggregators = models.ManyToManyField(Aggregator, through='TaxiDriverAggregator')

    def __str__(self):
        """
        Return name and surname of the taxi driver.

        Returns:
            self.first_name self.last_name: Driver's name and surname
        """
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Taxi Driver'
        verbose_name_plural = 'Taxi Drivers'


class TaxiDriverAggregator(models.Model):
    """Model representing Taxi Driver to Aggregator relationship."""

    taxi_driver = models.ForeignKey(TaxiDriver, on_delete=models.CASCADE)
    aggregator = models.ForeignKey(Aggregator, on_delete=models.CASCADE)

    class Meta:
        ordering = ['aggregator', 'taxi_driver']
        verbose_name = 'Taxi Driver Aggregator Relationship'
        verbose_name_plural = 'Taxi Driver Aggregator Relationships'
        unique_together = ('taxi_driver', 'aggregator')


class Order(UUIDMixin, CreatedMixin):
    """Model representing an Order."""

    name = models.TextField(null=False, blank=False, unique=True, max_length=TITLE_LENGTH_MAX)
    date = models.DateTimeField(default=get_datetime, validators=[validate_future_date])
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[check_positive])
    pickup_address = models.TextField(null=True, blank=True, max_length=ADDRESS_LENGTH_MAX)
    destination_address = models.TextField(null=True, blank=True, max_length=ADDRESS_LENGTH_MAX)
    taxi_driver = models.ForeignKey(TaxiDriver, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        """
        Return the name of the order.

        Returns:
            self.name: Order's name as a string
        """
        return f'{self.name}'

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['date']
