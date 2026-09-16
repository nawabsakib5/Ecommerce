from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Wishlist, Notification
from item.models import Item, Category

User = get_user_model()


def make_user(username, password='Pass123!', **kwargs):
    return User.objects.create_user(
        username=username,
        password=password,
        email=f'{username}@test.com',
        **kwargs
    )


class SignupViewTest(TestCase):
    """Signup flow test"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('core:signup')

    def test_signup_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_sees_signup_page(self):
        """Signup page সবার জন্য accessible"""
        response = self.client.get(self.url)
        self.assertContains(response, 'form')


class ChangePasswordViewTest(TestCase):
    """changePass view test"""

    def setUp(self):
        self.client = Client()
        self.user = make_user('testuser')
        self.url = reverse('core:changePass')

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [301, 302])

    def test_page_loads_when_logged_in(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_wrong_old_password_rejected(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.post(self.url, {
            'old_pass': 'WrongPass!',
            'new_pass': 'NewPass123!',
            'con_pass': 'NewPass123!',
        })
        self.user.refresh_from_db()
        # Password পরিবর্তন হয়নি
        self.assertTrue(self.user.check_password('Pass123!'))

    def test_mismatched_passwords_rejected(self):
        self.client.login(username='testuser', password='Pass123!')
        self.client.post(self.url, {
            'old_pass': 'Pass123!',
            'new_pass': 'NewPass123!',
            'con_pass': 'DifferentPass123!',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Pass123!'))

    def test_weak_password_rejected(self):
        """AUTH_PASSWORD_VALIDATORS enforce হচ্ছে কিনা"""
        self.client.login(username='testuser', password='Pass123!')
        self.client.post(self.url, {
            'old_pass': 'Pass123!',
            'new_pass': '123',
            'con_pass': '123',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Pass123!'))

    def test_valid_password_change_succeeds(self):
        self.client.login(username='testuser', password='Pass123!')
        response = self.client.post(self.url, {
            'old_pass': 'Pass123!',
            'new_pass': 'NewStrongPass99!',
            'con_pass': 'NewStrongPass99!',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass99!'))


class WishlistTest(TestCase):
    """Wishlist toggle test"""

    def setUp(self):
        self.client = Client()
        self.user = make_user('buyer1')
        self.seller = make_user('seller1')
        self.category = Category.objects.create(name='Shirts')
        self.item = Item.objects.create(
            category=self.category,
            user=self.seller,
            name='Test Shirt',
            original_price=500,
            stock_count=5,
            status='active',
        )

    def test_toggle_wishlist_add(self):
        self.client.login(username='buyer1', password='Pass123!')
        url = reverse('core:toggle_wishlist', kwargs={'item_id': self.item.pk})
        self.client.get(url)
        self.assertTrue(
            Wishlist.objects.filter(user=self.user, item=self.item).exists()
        )

    def test_toggle_wishlist_remove(self):
        Wishlist.objects.create(user=self.user, item=self.item)
        self.client.login(username='buyer1', password='Pass123!')
        url = reverse('core:toggle_wishlist', kwargs={'item_id': self.item.pk})
        self.client.get(url)
        self.assertFalse(
            Wishlist.objects.filter(user=self.user, item=self.item).exists()
        )

    def test_wishlist_requires_login(self):
        url = reverse('core:toggle_wishlist', kwargs={'item_id': self.item.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [301, 302])


class FrozenUserTest(TestCase):
    """Frozen user login block test"""

    def setUp(self):
        self.client = Client()
        self.user = make_user('frozenuser')
        self.user.is_frozen = True
        self.user.save()

    def test_frozen_user_cannot_login(self):
        response = self.client.post(reverse('core:login'), {
            'username': 'frozenuser',
            'password': 'Pass123!',
        })
        # Login fail করবে বা home-এ যাবে না
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class NotificationTest(TestCase):
    """Notification model test"""

    def setUp(self):
        self.user = make_user('testuser')

    def test_notification_created(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Test',
            message='Test message',
            notification_type='general',
        )
        self.assertEqual(notif.is_read, False)
        self.assertEqual(str(notif), f"{self.user.username} — Test")

    def test_notifications_marked_read_on_view(self):
        Notification.objects.create(
            user=self.user, title='T1', message='M1', notification_type='general'
        )
        Notification.objects.create(
            user=self.user, title='T2', message='M2', notification_type='general'
        )
        self.client.login(username='testuser', password='Pass123!')
        self.client.get(reverse('core:notifications'))
        unread = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)


class AdminDashboardAccessTest(TestCase):
    """Admin dashboard access control test"""

    def setUp(self):
        self.client = Client()
        self.buyer = make_user('buyer1', user_type='Buyer')
        self.admin = make_user('admin1', is_staff=True, is_superuser=True)

    def test_buyer_cannot_access_admin_dashboard(self):
        self.client.login(username='buyer1', password='Pass123!')
        response = self.client.get(reverse('dashboard:admin'))
        # Redirect হবে — access নেই
        self.assertIn(response.status_code, [302, 403])
        self.assertNotEqual(response.status_code, 200)

    def test_admin_can_access_admin_dashboard(self):
        self.client.login(username='admin1', password='Pass123!')
        response = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(response.status_code, 200)