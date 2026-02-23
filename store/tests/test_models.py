import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from django.test import TestCase
from store.models import Category, Product, CartItem, Order, OrderItem, Cart
import django
django.setup()
from django.contrib.auth.models import User

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Электроника", description="Товары для дома")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Электроника")
        self.assertEqual(self.category.description, "Товары для дома")

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Одежда", description="Модные вещи")
        self.product = Product.objects.create(
            name="Футболка",
            category=self.category,
            price=19.99,
            stock=50,
            description="Классная футболка"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Футболка")
        self.assertEqual(self.product.price, 19.99)
        self.assertTrue(self.product.is_available)  # Проверяем доступность

@pytest.mark.django_db
def test_product_update_availability():
    category = Category.objects.create(name="Одежда")
    product = Product.objects.create(name="Куртка", category=category, price=100.00, stock=1)

    product.update_availability()
    assert product.is_available is True  # ✅ Доступен

    product.stock = 0
    product.update_availability()
    assert product.is_available is False  # ✅ Нет в наличии

@pytest.mark.django_db
def test_cart_total_price():
    user = User.objects.create(username="testuser")
    cart, _ = Cart.objects.get_or_create(user=user)

    category = Category.objects.create(name="Электроника")
    product1 = Product.objects.create(name="Телефон", category=category, price=500.00, stock=10)
    product2 = Product.objects.create(name="Ноутбук", category=category, price=1000.00, stock=5)

    CartItem.objects.create(cart=cart, product=product1, quantity=2)  # ✅ 2 шт. по 500
    CartItem.objects.create(cart=cart, product=product2, quantity=1)  # ✅ 1 шт. по 1000

    assert cart.get_total_price() == 2000.00  # ✅ Проверяем сумму

@pytest.mark.django_db
def test_order_creation():
    user = User.objects.create(username="testuser")
    order = Order.objects.create(user=user, recipient_name="Клиент", address="Москва", phone_number="1234567890")

    category = Category.objects.create(name="Бытовая техника")
    product = Product.objects.create(name="Чайник", category=category, price=50.00, stock=5)

    order_item = OrderItem.objects.create(order=order, product=product, quantity=3)

    assert order.items.count() == 1  # ✅ Проверяем, что товар добавлен
    assert order_item.product.name == "Чайник"
    assert order_item.quantity == 3

@pytest.mark.django_db
def test_product_str():
    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(name="Телефон", category=category, price=1000, stock=5)
    expected_str = f"Телефон, {product.price} (Доступен)"
    assert str(product) == expected_str

@pytest.mark.django_db
def test_cart_item_total_price():
    user = User.objects.create(username="testuser")
    cart, _ = Cart.objects.get_or_create(user=user)  # ✅ Если корзина уже есть, используем существующую

    category = Category.objects.create(name="Игрушки")
    product = Product.objects.create(name="Кубики", category=category, price=25.00, stock=10)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=3)

    assert cart_item.get_total_price() == 75.00  # ✅ Проверяем расчет
