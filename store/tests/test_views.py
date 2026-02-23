import sys
import os
import django
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from store.models import Product, Category, Cart, CartItem, ProductImage
from django.contrib.auth.models import User
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Устанавливаем Django настройки, если они еще не загружены
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopmy.settings")
django.setup()  # ✅ Загрузка Django перед тестами

class StoreViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.category = Category.objects.create(name="Электроника")
        self.product = Product.objects.create( name="Лаптоп", price=1500.00, stock=5, category=self.category)
        self.cart, _ = Cart.objects.get_or_create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.product_image = ProductImage.objects.create(
            image=SimpleUploadedFile("test.jpg", b"fake_image_content", content_type="image/jpeg")
        )
        self.product.product_images.add(self.product_image)


@pytest.mark.django_db
def test_product_list_view(client):
    response = client.get(reverse("product_list"))
    assert response.status_code == 200  # ✅ Проверяем, что страница загружается


@pytest.mark.django_db
def test_product_detail_view(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)  # 🔑 Авторизация

    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(name="Лаптоп", price=1500.00, stock=5, category=category)

    response = client.get(reverse("product_detail", args=[product.id]))
    assert response.status_code == 200  # ✅ Проверяем, что продукт можно открыть


@pytest.mark.django_db
def test_cart_view(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)

    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(
        name="Лаптоп",
        price=1500.00,
        stock=5,
        category=category,
        photo = SimpleUploadedFile("test.jpg", b"fake_image_content", content_type="image/jpeg")
    )
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)

    response = client.get(reverse("cart_view"))
    assert response.status_code == 200  # ✅ Проверяем, что корзина загружается


@pytest.mark.django_db
def test_add_to_cart(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)

    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(name="Лаптоп", price=1500.00, stock=5, category=category)

    response = client.post(reverse("add_to_cart", args=[product.id]))
    assert response.status_code == 200  # ✅ Проверяем, что продукт добавляется


@pytest.mark.django_db
def test_place_order(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)

    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(name="Лаптоп", price=1500.00, stock=5, category=category)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)

    response = client.post(reverse("place_order"), {
        "recipient_name": "Тестовый клиент",
        "address": "Тестовый адрес",
        "phone_number": "1234567890"
    })
    assert response.status_code == 200  # ✅ Проверяем, что заказ оформляется


@pytest.mark.django_db
def test_signup(client):
    response = client.post(reverse("signup"), {
        "username": "newuser",
        "password1": "SuperSecret123!",
        "password2": "SuperSecret123!"
    })
    assert response.status_code == 200  # ✅ Проверяем, что регистрация проходит

@pytest.mark.django_db
def test_place_order_unauthorized(client):
    response = client.post(reverse("place_order"), {
        "recipient_name": "Тестовый клиент",
        "address": "Тестовый адрес",
        "phone_number": "1234567890"
    })
    assert response.status_code == 302  # ✅ Ожидаем `Forbidden`
    assert "/login/" in response.url

@pytest.mark.django_db
def test_place_order_empty_cart(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)

    response = client.post(reverse("place_order"), {
        "recipient_name": "Тестовый клиент",
        "address": "Тестовый адрес",
        "phone_number": "1234567890"
    })
    json_response = response.json()

    assert response.status_code == 400  # ✅ Ожидаем ошибку
    assert json_response["error"] == "Корзина пуста!"

@pytest.mark.django_db
def test_update_cart_item_invalid(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)

    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(name="Лаптоп", price=1500.00, stock=5, category=category)
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)

    invalid_values = ["0", "-1", "abc"]
    for value in invalid_values:
        response = client.post(reverse("update_cart_item", args=[cart_item.id]), {"quantity": value})
        assert response.status_code == 400  # ✅ Ожидаем ошибку
        assert response.json()["error"] == "Неверное значение"

@pytest.mark.django_db
def test_add_to_cart_json_response(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)

    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(name="Лаптоп", price=1500.00, stock=5, category=category)

    response = client.post(reverse("add_to_cart", args=[product.id]))
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["success"] is True
    assert json_response["message"] == "Товар добавлен в корзину!"

@pytest.mark.django_db
def test_place_order_json_response(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)

    category = Category.objects.create(name="Электроника")
    product = Product.objects.create(name="Лаптоп", price=1500.00, stock=5, category=category)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)

    response = client.post(reverse("place_order"), {
        "recipient_name": "Тестовый клиент",
        "address": "Тестовый адрес",
        "phone_number": "1234567890"
    })
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["success"] is True
    assert "redirect_url" in json_response

@pytest.mark.django_db
def test_clear_cart(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=Product.objects.create(name="Товар", price=100, stock=10, category=Category.objects.create(name="Тест")))

    response = client.post(reverse("clear_cart"))
    assert response.status_code == 302  # ✅ Проверяем редирект
    assert cart.items.count() == 0  # ✅ Корзина должна быть пустой

@pytest.mark.django_db
def test_clear_cart(client, django_user_model):
    user = django_user_model.objects.create(username="testuser")
    client.force_login(user)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=Product.objects.create(name="Товар", price=100, stock=10, category=Category.objects.create(name="Тест")))

    response = client.post(reverse("clear_cart"))
    assert response.status_code == 302  # ✅ Проверяем редирект
    assert cart.items.count() == 0  # ✅ Корзина должна быть пустой
