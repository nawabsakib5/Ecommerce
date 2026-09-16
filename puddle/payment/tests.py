from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from item.models import Item, Category
from payment.models import Transaction, Order, Coupon, CouponUsage

User = get_user_model()


def make_user(username, password='Pass123!', email=None, **kwargs):
    return User.objects.create_user(
        username=username,
        password=password,
        email=email or f'{username}@test.com',
        **kwargs
    )


def make_item(user, category, name='Test Shirt', price=500, stock=10):
    return Item.objects.create(
        category=category,
        user=user,
        name=name,
        original_price=Decimal(str(price)),
        stock_count=stock,
        status='active',
    )


class OrderConfirmPaymentTest(TestCase):
    """confirm_payment() — stock deduction ও race condition test"""

    def setUp(self):
        self.buyer = make_user('buyer1')
        self.seller = make_user('seller1')
        self.category = Category.objects.create(name='Shirts')
        self.item = make_item(self.seller, self.category, stock=5)

        self.transaction = Transaction.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            item=self.item,
            payment_type='cod',
            amount=Decimal('580'),
            status='pending',
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            item=self.item,
            transaction=self.transaction,
            quantity=2,
            unit_price=Decimal('500'),
            total_amount=Decimal('580'),
            delivery_name='Test Buyer',
            delivery_phone='01700000000',
            delivery_address='Dhaka',
            status='pending_payment',
        )

    def test_confirm_payment_deducts_stock(self):
        result = self.order.confirm_payment()
        self.assertTrue(result)
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_count, 3)

    def test_confirm_payment_sets_status_payment_confirmed(self):
        self.order.confirm_payment()
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'payment_confirmed')

    def test_confirm_payment_fails_if_insufficient_stock(self):
        self.item.stock_count = 1
        self.item.save()
        result = self.order.confirm_payment()
        self.assertFalse(result)
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_count, 1)  # unchanged

    def test_confirm_payment_idempotent(self):
        """দুইবার call করলে stock দুইবার deduct হবে না"""
        self.order.confirm_payment()
        self.order.confirm_payment()
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_count, 3)

    def test_restore_stock_increases_stock(self):
        self.order.confirm_payment()
        self.order.restore_stock()
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_count, 5)

    def test_restore_stock_idempotent(self):
        """দুইবার restore করলে stock দুইবার বাড়বে না"""
        self.order.confirm_payment()
        self.order.restore_stock()
        self.order.restore_stock()
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_count, 5)


class CheckoutViewTest(TestCase):
    """Checkout page access control test"""

    def setUp(self):
        self.client = Client()
        self.buyer = make_user('buyer1', user_type='Buyer')
        self.seller = make_user('seller1', user_type='Seller')
        self.category = Category.objects.create(name='Shirts')
        self.item = make_item(self.seller, self.category)

    def test_checkout_requires_login(self):
        url = reverse('payment:checkout', kwargs={'item_pk': self.item.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])
        self.assertIn('/login', response['Location'])

    def test_buyer_can_access_checkout(self):
        self.client.login(username='buyer1', password='Pass123!')
        url = reverse('payment:checkout', kwargs={'item_pk': self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_seller_cannot_buy_own_item(self):
        self.client.login(username='seller1', password='Pass123!')
        url = reverse('payment:checkout', kwargs={'item_pk': self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_sold_item_not_available(self):
        self.item.is_sold = True
        self.item.status = 'sold'
        self.item.save()
        self.client.login(username='buyer1', password='Pass123!')
        url = reverse('payment:checkout', kwargs={'item_pk': self.item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class InitiatePaymentTest(TestCase):
    """initiate_payment — price calculation ও coupon test"""

    def setUp(self):
        self.client = Client()
        self.buyer = make_user('buyer1', user_type='Buyer')
        self.seller = make_user('seller1', user_type='Seller')
        self.category = Category.objects.create(name='Shirts')
        self.item = make_item(self.seller, self.category, price=500, stock=10)

    def _post_payment(self, extra=None):
        data = {
            'payment_type': 'cod',
            'delivery_name': 'Test Buyer',
            'delivery_phone': '01700000000',
            'delivery_address': '56/L Dhaka',
            'delivery_zone': 'dhaka',
            'quantity': '1',
        }
        if extra:
            data.update(extra)
        self.client.login(username='buyer1', password='Pass123!')
        url = reverse('payment:initiate', kwargs={'item_pk': self.item.pk})
        return self.client.post(url, data)

    def test_cod_order_created_with_correct_amount(self):
        self._post_payment()
        order = Order.objects.filter(buyer=self.buyer).first()
        self.assertIsNotNone(order)
        # ৳500 item + ৳80 delivery = ৳580
        self.assertEqual(order.total_amount, Decimal('580'))

    def test_outside_dhaka_delivery_charge(self):
        self._post_payment({'delivery_zone': 'outside'})
        order = Order.objects.filter(buyer=self.buyer).first()
        # ৳500 + ৳150 = ৳650
        self.assertEqual(order.total_amount, Decimal('650'))

    def test_coupon_discount_applied_correctly(self):
        """Coupon discount server-side apply হচ্ছে কিনা"""
        now = timezone.now()
        coupon = Coupon.objects.create(
            code='SAVE50',
            discount_type='fixed',
            discount_value=Decimal('50'),
            min_order_amount=Decimal('100'),
            is_active=True,
            usage_limit=10,
            per_user_limit=1,
            valid_from=now - timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=1),
        )
        self._post_payment({'coupon_code': 'SAVE50'})
        order = Order.objects.filter(buyer=self.buyer).first()
        # ৳500 + ৳80 - ৳50 = ৳530
        self.assertEqual(order.total_amount, Decimal('530'))

    def test_invalid_coupon_ignored(self):
        """Invalid coupon দিলে full price নেয়"""
        self._post_payment({'coupon_code': 'FAKECODE'})
        order = Order.objects.filter(buyer=self.buyer).first()
        self.assertEqual(order.total_amount, Decimal('580'))

    def test_missing_delivery_info_rejected(self):
        self.client.login(username='buyer1', password='Pass123!')
        url = reverse('payment:initiate', kwargs={'item_pk': self.item.pk})
        response = self.client.post(url, {
            'payment_type': 'cod',
            'delivery_name': '',
            'delivery_phone': '',
            'delivery_address': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)


class CouponModelTest(TestCase):
    """Coupon model validation test"""

    def setUp(self):
        now = timezone.now()
        self.coupon = Coupon.objects.create(
            code='TEST10',
            discount_type='percent',
            discount_value=Decimal('10'),
            min_order_amount=Decimal('200'),
            is_active=True,
            usage_limit=5,
            per_user_limit=1,
            valid_from=now - timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=1),
        )

    def test_coupon_is_valid(self):
        self.assertTrue(self.coupon.is_valid())

    def test_expired_coupon_is_invalid(self):
        self.coupon.valid_until = timezone.now() - timezone.timedelta(days=1)
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())

    def test_usage_limit_reached_is_invalid(self):
        self.coupon.used_count = 5
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())

    def test_percent_discount_calculation(self):
        discount = self.coupon.get_discount_amount(Decimal('1000'))
        self.assertEqual(discount, Decimal('100'))

    def test_percent_discount_with_max_cap(self):
        self.coupon.max_discount_amount = Decimal('50')
        self.coupon.save()
        discount = self.coupon.get_discount_amount(Decimal('1000'))
        self.assertEqual(discount, Decimal('50'))

    def test_fixed_discount_cannot_exceed_order_amount(self):
        coupon = Coupon.objects.create(
            code='FIXED500',
            discount_type='fixed',
            discount_value=Decimal('500'),
            min_order_amount=Decimal('0'),
            is_active=True,
            usage_limit=5,
            per_user_limit=1,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
        )
        discount = coupon.get_discount_amount(Decimal('100'))
        self.assertEqual(discount, Decimal('100'))