from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Добавляем поле email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # Определяем порядок полей

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован!")
        return email



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['recipient_name', 'address', 'phone_number', 'email']  # Поля формы
