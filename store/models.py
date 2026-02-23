from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import now


# Модель категории продукта
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}, {self.description}"

# Модель продукта
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='product_images/', blank=True, null=True)  # Новое поле
    stock = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)  # ✅ Добавляем доступность
    images = models.ManyToManyField('ProductImage', blank=True, related_name='product_photos')


    def update_availability(self):
        self.is_available = self.stock > 0  # ✅ Если товара нет, он недоступен
        self.save()


    def __str__(self):
        return f"{self.name}, {self.price} ({'Доступен' if self.is_available else 'Нет в наличии'})"

        # return f" {self.name}, {self.price}"


class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return f"Фото для {self.product.name}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="cart")
    session_key = models.CharField(max_length=32, null=True, blank=True)  # Для анонимных пользователей

    def __str__(self):
        return f"Корзина {self.user.username if self.user else 'Анонимного пользователя'}"

    def get_total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

        def __str__(self):
            return f"Корзина {self.user.username}"

# Модель товаров для корзины (Item в корзине)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # Установите связь
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        if self.product:
            return f"{self.quantity} x {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Связь с пользователем
    recipient_name = models.CharField(max_length=100)  # Имя получателя
    address = models.TextField()  # Адрес доставки
    phone_number = models.CharField(max_length=15)  # Номер телефона
    email = models.EmailField(blank=True, null=True)  # Email
    created_at = models.DateTimeField(auto_now_add=True)  # Дата заказа



    def __str__(self):
        return f"Заказ от {self.recipient_name} ({self.created_at:%d.%m.%Y})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} для заказа {self.order.id}"


# Модель оплаты
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Оплата {self.user.username}: {self.amount} ({self.status})"




