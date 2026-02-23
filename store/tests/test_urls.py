from django.urls import reverse, resolve
from store.views import product_list, cart_view, signup

def test_product_list_url():
    assert resolve(reverse("product_list")).func == product_list  # ✅ Проверяем маршрут

def test_cart_view_url():
    assert resolve(reverse("cart_view")).func == cart_view  # ✅ Проверяем маршрут

def test_signup_url():
    assert resolve(reverse("signup")).func == signup  # ✅ Проверяем маршрут
