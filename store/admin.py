
from django.contrib import admin
from .models import Product, Category, Extra, Sauce


# class CartAdmin(admin.ModelAdmin):
#     def save_model(self, request, obj, form, change):
#         if not obj.items.exists():
#             raise ValueError("Корзина не может быть пустой!")
#         super().save_model(request, obj, form, change)
#
# admin.site.register(Cart, CartAdmin)
# admin.site.register(CartItem)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Extra)
admin.site.register(Sauce)
# admin.site.register(Payment)
