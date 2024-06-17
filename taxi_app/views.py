"""Module containing views for this Django application."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from taxi_app.forms import AggregatorForm, OrderForm, TaxiDriverForm
from taxi_app.models import Aggregator, Order, TaxiDriver, TaxiDriverAggregator
from taxi_app.serializers import AggregatorSerializer, OrderSerializer, TaxiDriverSerializer, TaxiDriverAggregatorSerializer

ERROR = 'error'
TITLE = 'title'
AGGREGATOR = 'aggregator'
TAXI_DRIVER = 'taxi_driver'
ORDER = 'order'
POST = 'POST'
FORM = 'form'


class UserAdminPermission(permissions.BasePermission):
    """Defines admin permission."""

    _safe_methods = ['GET', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view) -> bool:
        """Ensure that user is authenticated.

        Args:
            request: Sent request.
            view: View object.

        Returns:
            bool: True if user is authenticated
        """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, objec) -> bool:
        """Ensure that user has permission to modify object or is a staff.

        Args:
            request: Sent request.
            view: View object.
            objec: Object to check permissions.

        Returns:
            bool: True if user has permission
        """
        if request.method in self._safe_methods:
            return True
        return request.user.is_staff or objec.user == request.user


class AggregatorViewSet(viewsets.ModelViewSet):
    """Defines viewset for Aggregator module."""

    queryset = Aggregator.objects.all()
    serializer_class = AggregatorSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """Save user who created the aggregator.

        Args:
            serializer (serializers.Serializer): Serializer object.
        """
        serializer.save(user=self.request.user)


class TaxiDriverViewSet(viewsets.ModelViewSet):
    """Defines viewset for Taxi Driver module."""

    queryset = TaxiDriver.objects.all()
    serializer_class = TaxiDriverSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """Save user who created the taxi driver.

        Args:
            serializer (serializers.Serializer): Serializer object.
        """
        serializer.save(user=self.request.user)


class TaxiDriverAggregatorViewSet(viewsets.ModelViewSet):
    """Defines viewset for Taxi Driver Aggregator module."""

    queryset = TaxiDriverAggregator.objects.all()
    serializer_class = TaxiDriverAggregatorSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """Save user who created the driver to aggregator relationship.

        Args:
            serializer (serializers.Serializer): Serializer object.
        """
        serializer.save()


class OrderViewSet(viewsets.ModelViewSet):
    """Defines viewset for Order module."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """Save user who created the order.

        Args:
            serializer (serializers.Serializer): Serializer object.
        """
        taxi_driver = TaxiDriver.objects.get(user=self.request.user)
        serializer.save(taxi_driver=taxi_driver)


class UserRegistrationView(APIView):
    """Lets users register in the application."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Register a new user.

        Args:
            request: Sent request.

        Returns:
            HttpResponse: Register the user
        """
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(
                {ERROR: 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create_user(username=username, password=password)
            token = Token.objects.create(user=user)
        else:
            return Response({ERROR: 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        login(request=request, user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

    def get(self, request):
        """Load registration page.

        Args:
            request : Sent request.

        Returns:
            HttpResponse: Load the registration page.
        """
        return render(request, 'register.html')


class UserLoginView(APIView):
    """Lets users log in the application."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Log in a user.

        Args:
            request: Sent request.

        Returns:
            HttpResponse: Log in the user.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(
                {ERROR: 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({ERROR: 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({ERROR: 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
            token, _ = Token.objects.get_or_create(user=user)
        login(request=request, user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

    def get(self, request):
        """Load login page.

        Args:
            request : Sent request.

        Returns:
            HttpResponse: Load the login page.
        """
        return render(request, 'login.html')


def log_out(request):
    """Log user out of the application.

    Args:
        request : Sent request.

    Returns:
        HttpResponse: The main page.
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect('main_page')


def main_page(request):
    """Render the main page of the application.

    Args:
        request: Sent request.

    Returns:
        HttpRequest: Loads the main page.
    """
    pages = {
        'Агрегаторы': 'aggregators_page',
        'Таксисты': 'taxi_drivers_page',
        'Регистрация': 'register',
        'Получить токен': 'api_token',
    }
    return render(
        request,
        'main.html',
        context={
            'page': pages,
            TITLE: 'Главная страница',
            'user': request.user,
        },
    )


def aggregators_page(request):
    """Render page with the list of Aggregators.

    Args:
        request: Sent request.

    Returns:
        HttpResponse: Load the aggregators page.
    """
    return render(
        request,
        'aggregators.html',
        context={
            'aggregators': Aggregator.objects.all(),
            TITLE: 'Агрегаторы',
        },
    )


def aggregator_page(request, aggregator_id):
    """Render page with a single Aggregator.

    Args:
        request: Sent request.
        aggregator_id: ID of the aggregator.

    Returns:
        HttpResponse: Load the aggregator page.
    """
    return render(
        request,
        'entities/aggregator.html',
        context={
            AGGREGATOR: Aggregator.objects.get(id=aggregator_id),
            TITLE: 'Агрегатор',
        },
    )


def taxi_drivers_page(request):
    """Render page with the list of Taxi Drivers.

    Args:
        request: Sent request.

    Returns:
        HttpResponse: Load the taxi drivers page.
    """
    return render(
        request,
        'taxi_drivers.html',
        context={
            'taxi_drivers': TaxiDriver.objects.all(),
            TITLE: 'Таксисты',
        },
    )


def taxi_driver_page(request, taxi_driver_id):
    """Render page with a single Taxi Driver.

    Args:
        request: Sent request.
        taxi_driver_id: ID of the Taxi Driver.

    Returns:
        HttpResponse: Load the taxi driver page.
    """
    return render(
        request,
        'entities/taxi_driver.html',
        context={
            TAXI_DRIVER: TaxiDriver.objects.get(id=taxi_driver_id),
            TITLE: 'Таксист',
        },
    )


def orders_page(request):
    """Render page with the list of Orders.

    Args:
        request: Sent request.

    Returns:
        HttpResponse: Load the orders page.
    """
    return render(
        request,
        'orders.html',
        context={
            'orders': Order.objects.all(),
            TITLE: 'Заказы',
        },
    )


def order_page(request, order_id):
    """Render page with a single Order.

    Args:
        request: Sent request.
        order_id: ID of the Order.

    Returns:
        HttpResponse: Load the order page.
    """
    return render(
        request,
        'entities/order.html',
        context={
            ORDER: Order.objects.get(id=order_id),
            TITLE: 'Заказ',
        },
    )


def create_taxi_driver_view(request):
    """Create a new Taxi Driver.

    Args:
        request: Sent request.

    Returns:
        HttpResponse: Load the taxi driver creation page.
    """
    if request.user.is_authenticated:
        if request.method == POST:
            form = TaxiDriverForm(request.POST)
            if form.is_valid():
                taxi_driver = form.save(commit=False)
                taxi_driver.user = request.user
                taxi_driver.save()
                return redirect('taxi_drivers_page')
        else:
            form = TaxiDriverForm()
    else:
        messages.error(request, 'Вы должны войти в систему, чтобы добавить таксиста')
        form = TaxiDriverForm()
    return render(
        request,
        'forms/create_taxi_driver.html',
        context={
            FORM: form,
            TITLE: 'Создать таксиста',
        },
    )


def delete_taxi_driver(request, taxi_driver_id):
    """Delete a Taxi Driver.

    Args:
        request: Sent request.
        taxi_driver_id: ID of a Taxi Driver to be deleted.

    Returns:
        HttpResponse: Load taxi drivers page.
    """
    taxi_driver = get_object_or_404(TaxiDriver, id=taxi_driver_id)
    if request.user.is_staff or taxi_driver.user == request.user:
        taxi_driver.delete()
        return redirect('taxi_drivers_page')
    return redirect(TAXI_DRIVER, taxi_driver_id=taxi_driver.id)


def put_taxi_driver(request, taxi_driver_id):
    """Update Taxi Driver.

    Args:
        request: Sent request.
        taxi_driver_id: ID of a Taxi Driver to be modified.

    Returns:
        HttpResponse: Load taxi drivers updating page.
    """
    taxi_driver = get_object_or_404(TaxiDriver, id=taxi_driver_id)
    if request.user.is_staff or taxi_driver.user == request.user:
        if request.method == POST:
            form = TaxiDriverForm(request.POST, instance=taxi_driver)
            if form.is_valid():
                form.save()
                return redirect(TAXI_DRIVER, taxi_driver_id=taxi_driver.id)
        else:
            form = TaxiDriverForm(instance=taxi_driver)
    else:
        messages.error(request, 'У вас нет прав на изменение параметров этого таксиста')
        form = TaxiDriverForm(instance=taxi_driver)
    return render(
        request,
        'update/put_taxi_driver.html',
        context={
            FORM: form,
            TITLE: 'Изменить таксиста',
            TAXI_DRIVER: taxi_driver,
        },
    )


def create_order(request):
    """Create a new Order.

    Args:
        request: Sent request.

    Returns:
        HttpResponse: Load the order creation page.
    """
    if request.user.is_authenticated:
        if request.method == POST:
            form = OrderForm(request.POST)
            if form.is_valid():
                users_orders = Order.objects.filter(user=request.user).exists()
                if not request.user.is_staff and users_orders:
                    messages.error(request, 'Вы уже создали заказ')
                else:
                    order = form.save(commit=False)
                    order.user = request.user
                    order.save()
                    return redirect('orders_page')
        else:
            form = OrderForm()
    else:
        messages.error(request, 'Вы должны войти в систему, чтобы создать заказ')
        form = OrderForm()

    return render(
        request,
        'forms/create_order.html',
        context={
            FORM: form,
            TITLE: 'Создать заказ',
        },
    )


def delete_order(request, order_id):
    """Delete an Order.

    Args:
        request: Sent request.
        order_id: ID of an Order to be deleted.

    Returns:
        HttpResponse: Load orders page.
    """
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_staff or order.taxi_driver.user == request.user:
        order.delete()
        return redirect('orders_page')
    messages.error(request, 'У вас нет прав на удаление этого заказа')
    return redirect(ORDER, order_id=order.id)


def put_order(request, order_id):
    """Update Order.

    Args:
        request: Sent request.
        order_id: ID of an Order to be modified.

    Returns:
        HttpResponse: Load orders updating page.
    """
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_staff or order.taxi_driver.user == request.user:
        if request.method == POST:
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect(ORDER, order_id=order.id)
        else:
            form = OrderForm(instance=order)
    else:
        messages.error(request, 'У вас нет прав на изменение этого заказа')
        form = OrderForm(instance=order)
    return render(
        request,
        'update/put_order.html',
        context={
            FORM: form,
            TITLE: 'Изменить заказ',
            ORDER: order,
        },
    )


def create_aggregator(request):
    """Create a new Aggregator.

    Args:
        request: Sent request.

    Returns:
        HttpResponse: Load the aggregator page.
    """
    if request.user.is_authenticated:
        if request.method == POST:
            form = AggregatorForm(request.POST)
            if form.is_valid():
                users_aggregators = Aggregator.objects.filter(user=request.user).exists()
                if not request.user.is_staff and users_aggregators:
                    messages.error(request, 'Вы уже создали агрегатор')
                else:
                    aggregator = form.save(commit=False)
                    aggregator.user = request.user
                    aggregator.save()
                    return redirect('aggregators_page')
        else:
            form = AggregatorForm()
    else:
        messages.error(request, 'Вы должны войти в систему, чтобы создать агрегатор')
        form = AggregatorForm()

    return render(
        request,
        'forms/create_aggregator.html',
        context={
            FORM: form,
            TITLE: 'Создать агрегатор',
        },
    )


def delete_aggregator(request, aggregator_id):
    """Delete an Aggregator.

    Args:
        request: Sent request.
        aggregator_id: ID of an Aggregator to be deleted.

    Returns:
        HttpResponse: Load aggregators page.
    """
    aggregator = get_object_or_404(Aggregator, id=aggregator_id)
    if request.user.is_staff or aggregator.user == request.user:
        aggregator.delete()
        return redirect('aggregators_page')
    messages.error(request, 'У вас нет прав на удаление этого агрегатора')
    return redirect(AGGREGATOR, aggregator_id=aggregator.id)


def put_aggregator(request, aggregator_id):
    """Update Aggregator.

    Args:
        request: Sent request.
        aggregator_id: ID of a Aggregator to be modified.

    Returns:
        HttpResponse: Load aggregators updating page.
    """
    aggregator = get_object_or_404(Aggregator, id=aggregator_id)
    if request.user.is_staff or aggregator.user == request.user:
        if request.method == POST:
            form = AggregatorForm(request.POST, instance=aggregator)
            if form.is_valid():
                form.save()
                return redirect(AGGREGATOR, aggregator_id=aggregator.id)
        else:
            form = AggregatorForm(instance=aggregator)
    else:
        messages.error(request, 'У вас нет прав на изменение этого агрегатора')
        form = AggregatorForm(instance=aggregator)
    return render(
        request,
        'update/put_aggregator.html',
        context={
            FORM: form,
            TITLE: 'Изменить агрегатор',
            AGGREGATOR: aggregator,
        },
    )
