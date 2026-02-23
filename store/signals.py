from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Cart
from .utils import send_telegram_message  # Импортируем функцию
from django.contrib.auth.models import User

#
# @receiver(post_save, sender=Order)
# def notify_admin(sender, instance, **kwargs):
#     message = f"📦 Новый заказ от {instance.recipient_name}!\n🚚 Адрес: {instance.address}\n📞 Телефон: {instance.phone_number}"
#     send_telegram_message(message=message)


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
