"""Module for defining URLs of this Django project."""

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from taxi_app import views

router = routers.DefaultRouter()
router.register(r'aggregators', views.AggregatorViewSet)
router.register(r'taxi_drivers', views.TaxiDriverViewSet)
router.register(r'taxi_driver_aggregators', views.TaxiDriverAggregatorViewSet)
router.register(r'orders', views.OrderViewSet)

urlpatterns = [
    path(
        'admin/',
        admin.site.urls,
    ),
    path(
        'api/v1/',
        include(router.urls),
    ),
    path(
        'api-token-auth/',
        obtain_auth_token,
        name='api_token_auth',
    ),
    path(
        'login/',
        views.UserLoginView.as_view(),
        name='login',
    ),
    path(
        'logout/',
        views.log_out,
        name='logout',
    ),
    path(
        'register/',
        views.UserRegistrationView.as_view(),
        name='register',
    ),
    path(
        '',
        views.main_page,
        name='main_page',
    ),

    path(
        'taxi_drivers/',
        views.taxi_drivers_page,
        name='taxi_drivers_page',
    ),
    path(
        'taxi_driver/create/',
        views.create_taxi_driver_view,
        name='create_taxi_driver',
    ),
    path(
        'taxi_driver/<str:taxi_driver_id>/',
        views.taxi_driver_page,
        name='taxi_driver',
    ),
    path(
        'taxi_driver/delete/<str:taxi_driver_id>/',
        views.delete_taxi_driver,
        name='delete_taxi_driver',
    ),
    path(
        'taxi_driver/update/<str:taxi_driver_id>/',
        views.put_taxi_driver,
        name='put_taxi_driver',
    ),

    path(
        'aggregators/',
        views.aggregators_page,
        name='aggregators_page',
    ),
    path(
        'aggregator/<str:aggregator_id>/',
        views.aggregator_page,
        name='aggregator',
    ),
    path(
        'create_aggregator/',
        views.create_aggregator,
        name='create_aggregator',
    ),
    path(
        'delete_aggregator/<str:aggregator_id>/',
        views.delete_aggregator,
        name='delete_aggregator',
    ),
    path(
        'update_aggregator/<str:aggregator_id>/',
        views.put_aggregator,
        name='put_aggregator',
    ),

    path(
        'orders/',
        views.orders_page,
        name='orders_page',
    ),
    path(
        'order/<str:order_id>/',
        views.order_page,
        name='order',
    ),
    path(
        'create_order/',
        views.create_order,
        name='create_order',
    ),
    path(
        'delete_order/<str:order_id>/',
        views.delete_order,
        name='delete_order',
    ),
    path(
        'update_order/<str:order_id>/',
        views.put_order,
        name='put_order',
    ),
]
