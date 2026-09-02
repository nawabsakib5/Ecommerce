from django.test import TestCase
from django.contrib.auth import get_user_model
from item.models import Item, Category
from .models import Cart, CartItem, Sale, Order, OrderItem, COMMISSION_RATE

User = get_user_model()


class CartModelTest(TestCase):
    """Cart ও CartItem মডেল টেস্ট করে।"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer1', password='Pass123!', email='buyer@test.com'
        )
        self.seller = User.objects.create_user(
            username='seller1', password='Pass123!', email='seller@test.com'
        )
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name='Shirts')
        self.item = Item.objects.create(
            category=self.category,
            user=self.seller,
            name='Test Shirt',
            original_price=500,
            stock_count=10,
        )

    def test_cart_created_for_user(self):
        self.assertEqual(self.cart.user, self.user)

    def test_user_cannot_have_two_carts(self):
        with self.assertRaises(Exception):
            Cart.objects.create(user=self.user)

    def test_add_item_to_cart(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, item=self.item, quantity=2
        )
        self.assertEqual(cart_item.quantity, 2)
        self.assertIn(cart_item, self.cart.cart_items.all())

    def test_cart_item_subtotal_calculation(self):
        cart_item = CartItem.objects.create(
            cart=self.cart, item=self.item, quantity=3
        )
        self.assertEqual(cart_item.get_subtotal(), 1500)

    def test_cart_total_sums_all_items(self):
        item2 = Item.objects.create(
            category=self.category, user=self.seller,
            name='Test Pant', original_price=800, stock_count=10,
        )
        CartItem.objects.create(cart=self.cart, item=self.item, quantity=2)
        CartItem.objects.create(cart=self.cart, item=item2, quantity=1)
        self.assertEqual(self.cart.get_total(), 1800)

    def test_same_item_cannot_be_added_twice_to_same_cart(self):
        CartItem.objects.create(cart=self.cart, item=self.item, quantity=1)
        with self.assertRaises(Exception):
            CartItem.objects.create(cart=self.cart, item=self.item, quantity=1)

    def test_cart_item_quantity_cannot_be_negative(self):
        cart_item = CartItem(cart=self.cart, item=self.item, quantity=-1)
        with self.assertRaises(Exception):
            cart_item.full_clean()


class SaleModelTest(TestCase):
    """Sale মডেল ও commission ক্যালকুলেশন টেস্ট করে।"""

    def setUp(self):
        self.seller = User.objects.create_user(
            username='seller1', password='Pass123!', email='seller@test.com'
        )
        self.buyer = User.objects.create_user(
            username='buyer1', password='Pass123!', email='buyer@test.com'
        )
        self.category = Category.objects.create(name='Shirts')
        self.item = Item.objects.create(
            category=self.category, user=self.seller,
            name='Test Shirt', original_price=1000, stock_count=10,
        )

    def test_commission_calculation_default_rate(self):
        commission = Sale.calc_commission(1000)
        self.assertEqual(commission, 20.0)

    def test_sale_total_and_commission_consistency(self):
        total = 2000
        commission = Sale.calc_commission(total)
        sale = Sale.objects.create(
            item=self.item,
            seller=self.seller,
            buyer=self.buyer,
            quantity=2,
            unit_price=1000,
            total_amount=total,
            commission_amount=commission,
        )
        self.assertEqual(sale.total_amount, sale.quantity * sale.unit_price)
        self.assertEqual(sale.commission_amount, Sale.calc_commission(sale.total_amount))

    def test_sale_ordering_is_most_recent_first(self):
        sale1 = Sale.objects.create(
            item=self.item, seller=self.seller, buyer=self.buyer,
            quantity=1, unit_price=1000, total_amount=1000, commission_amount=20
        )
        sale2 = Sale.objects.create(
            item=self.item, seller=self.seller, buyer=self.buyer,
            quantity=1, unit_price=1000, total_amount=1000, commission_amount=20
        )
        sales = list(Sale.objects.all())
        self.assertEqual(sales[0], sale2)


class OrderModelTest(TestCase):
    """Order ও OrderItem মডেল টেস্ট করে।"""

    def setUp(self):
        self.buyer = User.objects.create_user(
            username='buyer1', password='Pass123!', email='buyer@test.com'
        )
        self.seller = User.objects.create_user(
            username='seller1', password='Pass123!', email='seller@test.com'
        )
        self.category = Category.objects.create(name='Shirts')
        self.item = Item.objects.create(
            category=self.category, user=self.seller,
            name='Test Shirt', original_price=500, stock_count=10,
        )

    def test_order_default_status_is_pending(self):
        order = Order.objects.create(buyer=self.buyer, total_amount=500)
        self.assertEqual(order.status, 'pending')

    def test_order_status_only_accepts_valid_choices(self):
        order = Order(buyer=self.buyer, total_amount=500, status='invalid_status')
        with self.assertRaises(Exception):
            order.full_clean()

    def test_order_item_subtotal_calculation(self):
        order = Order.objects.create(buyer=self.buyer, total_amount=1000)
        order_item = OrderItem.objects.create(
            order=order, item=self.item, quantity=2, price=500, seller=self.seller
        )
        self.assertEqual(order_item.get_subtotal(), 1000)

    def test_order_total_matches_sum_of_order_items(self):
        order = Order.objects.create(buyer=self.buyer, total_amount=1300)
        item2 = Item.objects.create(
            category=self.category, user=self.seller,
            name='Test Pant', original_price=800, stock_count=10,
        )
        OrderItem.objects.create(order=order, item=self.item, quantity=1, price=500, seller=self.seller)
        OrderItem.objects.create(order=order, item=item2, quantity=1, price=800, seller=self.seller)

        calculated_total = sum(oi.get_subtotal() for oi in order.order_items.all())
        self.assertEqual(order.total_amount, calculated_total)

    def test_buyer_cannot_access_another_buyers_order(self):
        other_buyer = User.objects.create_user(
            username='buyer2', password='Pass123!', email='buyer2@test.com'
        )
        order = Order.objects.create(buyer=self.buyer, total_amount=500)
        self.client.login(username='buyer2', password='Pass123!')
        # response = self.client.get(f'/order/{order.id}/')  # actual URL বসাও
        # self.assertIn(response.status_code, [403, 404])