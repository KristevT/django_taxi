"""Module for testing the whole Django application."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from taxi_app.models import Aggregator, Order, TaxiDriver
from taxi_app.views import (
    aggregator_page,
    aggregators_page,
    main_page,
    order_page,
    orders_page,
    taxi_driver_page,
    taxi_drivers_page,
    UserAdminPermission,
)
from taxi_app.forms import AggregatorForm


class TestTask(TestCase):
    """Test Taxi Driver model."""

    _user_creds = {
        'username': 'test',
        'password': 'test',
    }

    def setUp(self):
        """Set up test data for Taxi Driver model."""
        self.client = APIClient()
        self.user = User.objects.create(**self._user_creds)
        self.tocken = Token(user=self.user)
        self.client.force_authenticate(user=self.user, token=self.tocken)
        self.superuser = User.objects.create_superuser(
            username='test_admin',
            password='test_admin',
        )
        self.client.force_authenticate(
            user=self.superuser,
            token=Token.objects.create(user=self.superuser),
        )
        self.taxi_driver = TaxiDriver.objects.create(
            first_name='a',
            last_name='a',
            phone_number='+123',
            car='a',
            user=self.superuser,
        )
        self.aggregator = Aggregator.objects.create(
            name='a',
            phone='a',
            user=self.superuser,
        )
        self.order = Order.objects.create(
            name='a',
            date='2024-01-01',
            cost=1,
            pickup_address='a',
            destination_address='a',
            taxi_driver=self.taxi_driver,
        )

    def test_taxi_driver_list(self):
        """Test taxi driver list."""
        response = self.client.get('/api/v1/taxi_drivers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_taxi_driver_create(self):
        """Test taxi driver create."""
        response = self.client.post('/api/v1/taxi_drivers/', {
            'first_name': 'a',
            'last_name': 'a',
            'phone_number': '+123',
            'car': 'a',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn(
            response.data['id'],
            [str(taxi_driver.id) for taxi_driver in TaxiDriver.objects.all()],
        )

    def test_taxi_driver_update(self):
        """Test taxi driver update."""
        response = self.client.put(
            f'/api/v1/taxi_drivers/{self.taxi_driver.id}/', {
                'first_name': 'b',
                'last_name': 'b',
                'phone_number': '+234',
                'car': 'b',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(TaxiDriver.objects.get(first_name='b').last_name, 'b')
        self.assertEqual(TaxiDriver.objects.get(last_name='b').first_name, 'b')
        self.assertEqual(TaxiDriver.objects.get(first_name='b').phone_number, '+234')
        self.assertEqual(TaxiDriver.objects.get(first_name='b').car, 'b')

    def test_taxi_driver_delete(self):
        """Test taxi driver delete."""
        response = self.client.delete(f'/api/v1/taxi_drivers/{self.taxi_driver.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_aggregator_list(self):
        """Test aggregator list."""
        response = self.client.get('/api/v1/aggregators/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_aggregator_create(self):
        """Test aggregator create."""
        response = self.client.post('/api/v1/aggregators/', {'name': 'abc', 'phone': '+1234'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn(
            response.data['id'],
            [str(aggregator.id) for aggregator in Aggregator.objects.all()],
        )

    def test_aggregator_update(self):
        """Test aggregator update."""
        response = self.client.put(
            f'/api/v1/aggregators/{self.aggregator.id}/',
            {'name': 'b', 'phone': '+234'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(Aggregator.objects.get(name='b').phone, '+234')

    def test_aggregator_delete(self):
        """Test aggregator delete."""
        response = self.client.delete(f'/api/v1/aggregators/{self.aggregator.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_order_list(self):
        """Test order list."""
        response = self.client.get('/api/v1/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_create(self):
        """Test order create."""
        response = self.client.post(
            '/api/v1/orders/',
            {
                'name': 'abc',
                'date': '2024-01-01',
                'cost': 1,
                'pickup_address': 'a',
                'destination_address': 'a',
                'taxi_driver': self.taxi_driver.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn(response.data['id'], [str(order.id) for order in Order.objects.all()])

    def test_order_update(self):
        """Test order update."""
        response = self.client.put(
            f'/api/v1/orders/{self.order.id}/',
            {
                'name': 'b',
                'date': '2024-01-02',
                'cost': 2,
                'pickup_address': 'b',
                'destination_address': 'b',
                'taxi_driver': self.taxi_driver.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(Order.objects.get(name='b').cost, 2)
        self.assertEqual(Order.objects.get(pickup_address='b').destination_address, 'b')
        self.assertEqual(Order.objects.get(date='2024-01-02').cost, 2)

    def test_order_delete(self):
        """Test order delete."""
        response = self.client.delete(f'/api/v1/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_taxi_driver_aggregator_list(self):
        """Test taxi driver to aggregator list."""
        response = self.client.get('/api/v1/taxi_driver_aggregators/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_taxi_driver_aggregator(self):
        """Test create taxi driver to aggregator."""
        response = self.client.post(
            '/api/v1/taxi_driver_aggregators/',
            {
             'taxi_driver': self.taxi_driver.id,
             'aggregator': self.aggregator.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_already_exists(self):
        """Test user already exists."""
        response = self.client.post('/register/', {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'User already exists'})


class UserRegistrationViewTest(TestCase):
    """Tests user registration view."""

    def setUp(self):
        """Set up test data for user registration view."""
        self.client = Client()

    def test_registration_new_user(self):
        """Test registration new user."""
        response = self.client.post('/register/', {'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = get_user_model().objects.get(username='test_user')
        self.assertIsNotNone(user)
        token = Token.objects.get(user=user)
        self.assertEqual(response.json(), {'token': token.key})

    def test_registration_no_username(self):
        """Test registration no username."""
        response = self.client.post('/register/', {'password': 'test_password'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Username and password are required'})

    def test_logout_authenticated_user(self):
        """Test logout authenticated user."""
        user = get_user_model().objects.create_user(username='test_user', password='test_password')
        self.client.force_login(user)
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_unauthenticated_user(self):
        """Test logout unauthenticated user."""
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_get_registration(self):
        """Test get registration."""
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'register.html')

    def test_create_taxi_driver_view(self):
        """Test create taxi driver view."""
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client.login(username='test_user', password='password')
        initial_taxi_driver_count = TaxiDriver.objects.count()
        response = self.client.post(reverse('create_taxi_driver'), data={
            'first_name': 'a',
            'last_name': 'a',
            'phone_number': '+123',
            'car': 'a',
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(TaxiDriver.objects.count(), initial_taxi_driver_count + 1)
        response = self.client.get(reverse('taxi_drivers_page'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_taxi_driver(self):
        """Test delete taxi_driver."""
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client.login(username='test_user', password='password')
        taxi_driver = TaxiDriver.objects.create(
            first_name='a',
            last_name='a',
            phone_number='+123',
            car='a',
            user=self.user,
        )
        initial_taxi_driver_count = TaxiDriver.objects.count()
        response = self.client.post(reverse('delete_taxi_driver', args=[taxi_driver.id]))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(TaxiDriver.objects.count(), initial_taxi_driver_count - 1)

    def test_put_taxi_driver(self):
        """Test put taxi driver."""
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client.login(username='test_user', password='password')
        taxi_driver = TaxiDriver.objects.create(
            first_name='a',
            last_name='a',
            phone_number='+123',
            car='a',
            user=self.user,
        )
        initial_taxi_driver_count = TaxiDriver.objects.count()
        response = self.client.post(reverse('put_taxi_driver', args=[taxi_driver.id]), data={
            'first_name': 'b',
            'last_name': 'b',
            'phone_number': '+234',
            'car': 'b',
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(TaxiDriver.objects.count(), initial_taxi_driver_count)
        response = self.client.get(reverse('put_taxi_driver', args=[taxi_driver.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """Test create order."""
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client.login(username='test_user', password='password')
        taxi_driver = TaxiDriver.objects.create(
            first_name='a',
            last_name='a',
            phone_number='+123',
            car='a',
            user=self.user,
        )
        response = self.client.post(reverse('create_order'), data={
            'name': 'e',
            'date': '2024-01-02',
            'cost': 2,
            'pickup_address': 'wer',
            'destination_address': 'wer',
            'taxi_driver': taxi_driver,
        })
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_order(self):
        """Test delete order."""
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client.login(username='test_user', password='password')
        taxi_driver = TaxiDriver.objects.create(
            first_name='a',
            last_name='a',
            phone_number='+123',
            car='a',
            user=self.user,
        )
        order = Order.objects.create(
            name='abc',
            date='2024-01-01',
            cost=1,
            pickup_address='abc',
            destination_address='abc',
            taxi_driver=taxi_driver,
        )
        initial_order_count = Order.objects.count()
        response = self.client.post(reverse('delete_order', args=[order.id]))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Order.objects.count(), initial_order_count - 1)

    def test_put_order(self):
        """Test put order."""
        self.user = User.objects.create_user(username='test_user', password='password')
        self.client.login(username='test_user', password='password')
        taxi_driver = TaxiDriver.objects.create(
            first_name='a',
            last_name='a',
            phone_number='+123',
            car='a',
            user=self.user,
        )
        order = Order.objects.create(
            name='abc',
            date='2024-01-01',
            cost=1,
            pickup_address='abc',
            destination_address='abc',
            taxi_driver=taxi_driver,
        )
        initial_order_count = Order.objects.count()
        response = self.client.post(reverse('put_order', args=[order.id]), data={
            'name': 'def',
            'date': '2024-01-02',
            'cost': 2,
            'pickup_address': 'def',
            'destination_address': 'def',
            'taxi_driver': taxi_driver.id,
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Order.objects.count(), initial_order_count)
        response = self.client.get(reverse('put_order', args=[order.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserLoginViewTests(TestCase):
    """Tests user login view."""

    def setUp(self):
        """Set up test data for user login view."""
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='pass')

    def test_login_no_username_password(self):
        """Test login no username password."""
        response = self.client.post(reverse('login'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Username and password are required'})

    def test_login_no_user(self):
        """Test login no user."""
        response = self.client.post(reverse('login'), {'username': 'wrong', 'password': 'pass'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'User does not exist'})

    def test_login_wrong_password(self):
        """Test login wrong password."""
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Wrong password'})

    def test_login_success(self):
        """Test login success."""
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'pass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.json(), {'token': token.key})

    def test_get_login_page(self):
        """Test get login page."""
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')


class UserAdminPermissionTest(TestCase):
    """Tests user admin permission."""

    def setUp(self):
        """Set up test data for user admin permission."""
        self.factory = RequestFactory()
        self.permission = UserAdminPermission()
        self.view = None
        self.user = User.objects.create_user(username='test_user', password='password')

    def test_has_object_permission(self):
        """Test has object permission."""
        request = self.factory.get('/')
        request.user = self.user
        objc = None
        self.assertTrue(self.permission.has_object_permission(request, self.view, objc))


class ViewTestCase(TestCase):
    """Tests views."""

    def setUp(self):
        """Set up test data for views."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test_user', password='password')
        self.taxi_driver = TaxiDriver.objects.create(
            first_name='a',
            last_name='a',
            phone_number='+123',
            car='a',
            user=self.user,
        )
        self.aggregator = Aggregator.objects.create(name='a', phone='+123', user=self.user)
        self.order = Order.objects.create(
            name='abc',
            date='2024-01-01',
            cost=1,
            pickup_address='abc',
            destination_address='abc',
            taxi_driver=self.taxi_driver,
        )

    def test_taxi_drivers_page(self):
        """Test taxi drivers page."""
        request = self.factory.get('/taxi_drivers')
        response = taxi_drivers_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_taxi_driver_page(self):
        """Test taxi driver page."""
        request = self.factory.get(f'/taxi_driver/{self.taxi_driver.id}')
        response = taxi_driver_page(request, self.taxi_driver.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_aggregators_page(self):
        """Test aggregators page."""
        request = self.factory.get('/aggregators')
        response = aggregators_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_aggregator_page(self):
        """Test aggregator page."""
        request = self.factory.get(f'/aggregator/{self.aggregator.id}')
        response = aggregator_page(request, self.aggregator.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orders_page(self):
        """Test orders page."""
        request = self.factory.get('/orders')
        response = orders_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_page(self):
        """Test order page."""
        request = self.factory.get(f'/order/{self.order.id}')
        response = order_page(request, self.order.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_main_page(self):
        """Test main page."""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        response = main_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AggregatorViewTest(TestCase):
    """Tests aggregator view."""

    def setUp(self):
        """Set up test data for aggregator view."""
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.aggregator_data = {'name': 'a', 'phone': '+123', 'user': self.user}
        self.aggregator_form = AggregatorForm(data=self.aggregator_data)

    def test_create_aggregator(self):
        """Test create aggregator."""
        self.client.login(username='test_user', password='test_password')
        form = self.aggregator_form
        if form.is_valid():
            response = self.client.post(reverse('create_aggregator'), data=form.cleaned_data)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertRedirects(response, reverse('aggregators_page'))

    def test_create_aggregator_get_form(self):
        """Test create aggregator get form."""
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('create_aggregator'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'forms/create_aggregator.html')

    def test_put_aggregator_get_form(self):
        """Test put aggregator get form."""
        self.aggregator = Aggregator.objects.create(name='a', phone='+123', user=self.user)
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('put_aggregator', args=[self.aggregator.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'update/put_aggregator.html')

    def test_delete_aggregator(self):
        """Test delete aggregator."""
        self.aggregator = Aggregator.objects.create(name='a', phone='+1', user=self.user)
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(reverse('delete_aggregator', args=[self.aggregator.id]))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('aggregators_page'))

    def test_put_aggregator(self):
        """Test put aggregator."""
        self.aggregator = Aggregator.objects.create(name='a', phone='+1', user=self.user)
        self.client.login(username='test_user', password='test_password')
        form = self.aggregator_form
        if form.is_valid():
            response = self.client.post(
                reverse(
                    'put_aggregator',
                    args=[self.aggregator.id],
                ),
                data=form.cleaned_data,
            )
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertRedirects(response, reverse('aggregator', args=[self.aggregator.id]))

    def test_create_aggregator_not_authenticated(self):
        """Test create aggregator not authenticated."""
        response = self.client.post(reverse('create_aggregator'), data=self.aggregator_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Вы должны войти в систему, чтобы создать агрегатор')

    def test_delete_aggregator_no_permission(self):
        """Test delete aggregator no permission."""
        self.aggregator = Aggregator.objects.create(name='a', phone='+1', user=self.user)
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_aggregator', args=[self.aggregator.id]), follow=True)
        self.assertRedirects(
            response,
            expected_url=reverse(
                'aggregator', args=[self.aggregator.id],
            ),
            status_code=status.HTTP_302_FOUND, target_status_code=status.HTTP_200_OK,
        )
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'У вас нет прав на удаление этого агрегатора')

    def test_put_aggregator_no_permission(self):
        """Test put aggregator no permission."""
        self.aggregator = Aggregator.objects.create(name='b', phone='+3', user=self.user)
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(
            reverse(
                'put_aggregator',
                args=[self.aggregator.id],
            ),
            data=self.aggregator_data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'У вас нет прав на изменение этого агрегатора')

    def test_unauthenticated_user(self):
        """Test unauthenticated user."""
        response = self.client.get(reverse('create_taxi_driver'))
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'Вы должны войти в систему, чтобы добавить таксиста')


class OrderViewTests(TestCase):
    """Tests order view."""

    def setUp(self):
        """Set up test data for order view."""
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.taxi_driver = TaxiDriver.objects.create(
            first_name='b',
            last_name='b',
            phone_number='+234',
            car='b',
            user=self.user1,
        )
        self.aggregator1 = Aggregator.objects.create(name='a', phone='+1', user=self.user1)
        self.order = Order.objects.create(
            name='abc',
            date='2024-01-01',
            cost=1,
            pickup_address='abc',
            destination_address='abc',
            taxi_driver=self.taxi_driver,
        )

    def test_create_order_not_authenticated(self):
        """Test create order not authenticated."""
        response = self.client.post(reverse('create_order'))
        self.assertContains(response, 'Вы должны войти в систему, чтобы создать заказ')

    def test_delete_order_no_permission(self):
        """Test delete order no permission."""
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_order', args=[self.order.id]), follow=True)
        self.assertRedirects(
            response,
            expected_url=reverse('order', args=[self.order.id]),
            status_code=status.HTTP_302_FOUND, target_status_code=status.HTTP_200_OK,
        )
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'У вас нет прав на удаление этого заказа')

    def test_put_order_no_permission(self):
        """Test put order no permission."""
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('put_order', args=[self.order.id]))
        self.assertContains(response, 'У вас нет прав на изменение этого заказа')
