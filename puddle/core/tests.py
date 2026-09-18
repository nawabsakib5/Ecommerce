from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from core.models import Wishlist, Notification
from item.models import Item, Category

User = get_user_model()

# ✅ Test-এ Axes disable করো — test client request object আলাদা
@override_settings(
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
    AXES_ENABLED=False,
)
class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('core:signup')

    def test_signup_page_loads(self):
        # ✅ allauth SocialApp দরকার — Site + SocialApp তৈরি করো
        from allauth.socialaccount.models import SocialApp
        site = Site.objects.get_current()
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='test-client-id',
            secret='test-secret',
        )
        app.sites.add(site)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_signup_page_has_form(self):
        from allauth.socialaccount.models import SocialApp
        site = Site.objects.get_current()
        app = SocialApp.objects.create(
            provider='google', name='Google',
            client_id='test-client-id', secret='test-secret',
        )
        app.sites.add(site)
        response = self.client.get(self.url)
        self.assertContains(response, 'form')


@override_settings(
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
    AXES_ENABLED=False,
)
class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='Pass123!', email='test@test.com'
        )
        self.url = reverse('core:changePass')

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [301, 302])

    def test_page_loads_when_logged_in(self):
        # ✅ force_login — Axes bypass করে
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_wrong_old_password_rejected(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {
            'old_pass': 'WrongPass!',
            'new_pass': 'NewPass123!',
            'con_pass': 'NewPass123!',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Pass123!'))

    def test_mismatched_passwords_rejected(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {
            'old_pass': 'Pass123!',
            'new_pass': 'NewPass123!',
            'con_pass': 'DifferentPass123!',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Pass123!'))

    def test_weak_password_rejected(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {
            'old_pass': 'Pass123!',
            'new_pass': '123',
            'con_pass': '123',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Pass123!'))

    def test_valid_password_change_succeeds(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {
            'old_pass': 'Pass123!',
            'new_pass': 'NewStrongPass99!',
            'con_pass': 'NewStrongPass99!',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass99!'))


@override_settings(
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
    AXES_ENABLED=False,
)
class WishlistTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer1', password='Pass123!', email='buyer@test.com'
        )
        self.seller = User.objects.create_user(
            username='seller1', password='Pass123!', email='seller@test.com'
        )
        self.category = Category.objects.create(name='Shirts')
        self.item = Item.objects.create(
            category=self.category, user=self.seller,
            name='Test Shirt', original_price=Decimal('500'),
            stock_count=5, status='active',
        )

    def test_wishlist_requires_login(self):
        url = reverse('core:toggle_wishlist', kwargs={'item_id': self.item.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [301, 302])

    def test_toggle_wishlist_add(self):
        self.client.force_login(self.user)
        url = reverse('core:toggle_wishlist', kwargs={'item_id': self.item.pk})
        self.client.get(url)
        self.assertTrue(
            Wishlist.objects.filter(user=self.user, item=self.item).exists()
        )

    def test_toggle_wishlist_remove(self):
        Wishlist.objects.create(user=self.user, item=self.item)
        self.client.force_login(self.user)
        url = reverse('core:toggle_wishlist', kwargs={'item_id': self.item.pk})
        self.client.get(url)
        self.assertFalse(
            Wishlist.objects.filter(user=self.user, item=self.item).exists()
        )


class FrozenUserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='frozenuser', password='Pass123!', email='frozen@test.com'
        )
        self.user.is_frozen = True
        self.user.save()

    def test_frozen_user_is_frozen(self):
        """is_frozen field ঠিকমতো set হয়েছে কিনা"""
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_frozen)

    def test_active_user_is_not_frozen(self):
        active = User.objects.create_user(
            username='activeuser', password='Pass123!', email='active@test.com'
        )
        self.assertFalse(active.is_frozen)


class NotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='Pass123!', email='test@test.com'
        )

    def test_notification_created(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Test',
            message='Test message',
            notification_type='general',
        )
        self.assertEqual(notif.is_read, False)
        self.assertEqual(str(notif), f"{self.user.username} — Test")

    def test_notification_marked_read(self):
        notif = Notification.objects.create(
            user=self.user, title='T1', message='M1',
            notification_type='general'
        )
        self.client.force_login(self.user)
        self.client.get(reverse('core:notifications'))
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_multiple_notifications_all_marked_read(self):
        for i in range(3):
            Notification.objects.create(
                user=self.user, title=f'T{i}', message=f'M{i}',
                notification_type='general'
            )
        self.client.force_login(self.user)
        self.client.get(reverse('core:notifications'))
        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)


@override_settings(
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
    AXES_ENABLED=False,
)
class AdminDashboardAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username='buyer1', password='Pass123!',
            email='buyer@test.com', user_type='Buyer'
        )
        self.admin = User.objects.create_user(
            username='admin1', password='Pass123!',
            email='admin@test.com', is_staff=True, is_superuser=True
        )

    def test_buyer_cannot_access_admin_dashboard(self):
        self.client.force_login(self.buyer)
        response = self.client.get(reverse('dashboard:admin'))
        self.assertIn(response.status_code, [302, 403])
        self.assertNotEqual(response.status_code, 200)

    def test_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 200)