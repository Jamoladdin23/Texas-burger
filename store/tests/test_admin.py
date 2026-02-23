import sys
import os
from django.contrib import admin
from django.contrib.admin.sites import site
from store.models import Product, Category
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_admin_registration():
    assert Product in site._registry  # ✅ Проверяем, что модель зарегистрирована
    assert Category in site._registry  # ✅ Проверяем, что категория зарегистрирована
