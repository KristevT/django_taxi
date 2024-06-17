"""Module for defining form classes for Aggregator, TaxiDriver and Order models."""

from django import forms

from taxi_app.models import Aggregator, Order, TaxiDriver, TaxiDriverAggregator

MAX_LENGTH = 'max_length'
REQUIRED = 'required'
REQUIRED_FIELD = 'Поле обязательно для заполнения.'
UNIQUE = 'unique'
NAME = 'name'
TAXI_DRIVER = 'taxi_driver'


class TaxiDriverForm(forms.ModelForm):
    """Form class for Taxi Driver module."""

    class Meta:
        model = TaxiDriver
        fields = ['first_name', 'last_name', 'phone_number', 'car']
        labels = {
            'first_name': 'Имя таксиста',
            'last_name': 'Фамилия таксиста',
            'phone_number': 'Номер телефона',
            'car': 'Марка и номер машины',
        }
        error_messages = {
            'first_name': {
                MAX_LENGTH: 'Имя не должно превышать 50 символов.',
                REQUIRED: REQUIRED_FIELD,
            },
            'last_name': {
                MAX_LENGTH: 'Фамилия не должна превышать 50 символов.',
                REQUIRED: REQUIRED_FIELD,
            },
            'phone_number': {
                MAX_LENGTH: 'Номер не должен превышать 15 символов.',
            },
            'car': {
                MAX_LENGTH: 'Номер не должен превышать 100 символов.',
            },
        }


class OrderForm(forms.ModelForm):
    """Form class for Order module."""

    class Meta:
        model = Order
        fields = [NAME, 'date', 'cost', 'pickup_address', 'destination_address', 'taxi_driver']
        labels = {
            NAME: 'Название заказа',
            'date': 'Дата',
            'cost': 'Стоимость',
            'pickup_address': 'Адрес отправления',
            'destination_address': 'Адрес прибытия',
            TAXI_DRIVER: 'Таксист',
        }
        error_messages = {
            'name': {
                UNIQUE: 'Заказ с таким названием уже существует.',
                MAX_LENGTH: 'Название не должно превышать 100 символов.',
                REQUIRED: REQUIRED_FIELD,
            },
            'date': {
                REQUIRED: 'Поле обязательно для заполнения.',
            },
            'cost': {
                'max_digits': 'Стоимость не должна превышать 10 символов.',
                'decimal_places': 'Стоимость не должна содержать больше 2 символов после запятой.',
                REQUIRED: REQUIRED_FIELD,
            },
            'pickup_address': {
                MAX_LENGTH: 'Адрес не должен превышать 250 символов.',
            },
            'destination_address': {
                MAX_LENGTH: 'Адрес не должен превышать 250 символов.',
            },
            TAXI_DRIVER: {},
        }


class AggregatorForm(forms.ModelForm):
    """Form class for Aggregator module."""

    class Meta:
        model = Aggregator
        fields = [NAME, 'phone']
        labels = {
            NAME: 'Название',
            'phone': 'Номер телефона',
        }
        error_messages = {
            NAME: {
                UNIQUE: 'Агрегатор с таким названием уже существует.',
                MAX_LENGTH: 'Название не должно превышать 100 символов.',
                REQUIRED: REQUIRED_FIELD,
            },
            'phone': {
                UNIQUE: 'Агрегатор с таким номером телефона уже существует.',
                MAX_LENGTH: 'Номер не должен превышать 15 символов.',
                REQUIRED: REQUIRED_FIELD,
            },
        }


class TaxiDriverAggregatorForm(forms.ModelForm):
    """Form class for Taxi Driver to Aggregator module."""

    class Meta:
        model = TaxiDriverAggregator
        fields = [TAXI_DRIVER, 'aggregator']
        labels = {
            TAXI_DRIVER: 'Таксист',
            'aggregator': 'Агрегатор',
        }
        error_messages = {
            TAXI_DRIVER: {
                REQUIRED: REQUIRED_FIELD,
            },
            'aggregator': {
                REQUIRED: REQUIRED_FIELD,
            },
        }
