import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from django.test import TestCase
from store.forms import CustomUserCreationForm

@pytest.mark.django_db
def test_invalid_signup_form():
    form = CustomUserCreationForm(data={"username": "", "password1": "123", "password2": "123"})
    assert not form.is_valid()  # ✅ Ожидаем, что форма будет невалидной

@pytest.mark.django_db
def test_valid_signup_form():
    form = CustomUserCreationForm(data={
        "username": "newuser", "email": "test@example.com", "password1": "SuperSecret123!", "password2": "SuperSecret123!"})
    assert form.is_valid()  # ✅ Ожидаем, что форма пройдет валидацию
