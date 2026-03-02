from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import localtime
from .models import Cart, CartItem, Product, Category, Order, OrderItem
from .forms import CustomUserCreationForm, OrderForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .utils import send_telegram_message
from django.views.decorators.csrf import csrf_exempt


class CustomLoginView(LoginView):
    template_name = 'store/login.html'


def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if cart_item.cart and request.user.is_authenticated and cart_item.cart.user != request.user:
        return JsonResponse({'error': 'Нет доступа!'}, status=403)

    if request.method == 'POST':
        new_quantity = request.POST.get('quantity')

        if new_quantity and new_quantity.isdigit() and int(new_quantity) > 0:
            cart_item.quantity = int(new_quantity)
            cart_item.save()

            return redirect("cart_view")

    return JsonResponse({"success": False, "error": "Неверное значение"}, status=400)


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})


def category_detail(request, category_id):
    category = Category.objects.get(id=category_id)
    products = category.products.all()
    categories = Category.objects.all()  # 👈 ДОБАВИТЬ ЭТО

    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': products,
        'categories': categories  # 👈 И ПЕРЕДАТЬ
    })


# def category_detail(request, category_id):
#     category = Category.objects.get(id=category_id)
#     products = category.products.all()  # Получить все продукты в категории
#     return render(request, 'store/category_detail.html', {'category': category, 'products': products})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_images = product.images.all()  # ✅ Получаем все фото продукта
    photo_url = product.photo.url if product.photo else None
    return render(request, 'store/product_detail.html', {
        'product': product,
        'product_images': product_images,
        'photo_url': photo_url
    })


def add_to_cart(request, product_id):
    if not request.session.session_key:
        request.session.create()

    if request.method == "POST":
        try:
            product = get_object_or_404(Product, id=product_id)

            # 📌 Проверяем, авторизован ли пользователь
            if request.user.is_authenticated:
                cart, _ = Cart.objects.get_or_create(user=request.user)
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                session_key = request.session.session_key

                cart, _ = Cart.objects.get_or_create(session_key=session_key)  # ✅ Корзина для анонимных

            # 📌 Добавляем товар в корзину
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()

            return JsonResponse({"success": True, "quantity": sum(item.quantity for item in cart.items.all())
                                    , "message": "Товар добавлен в корзину!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Некорректный запрос"})


def cart_view(request):
    # Проверяем, авторизован ли пользователь
    if request.user.is_authenticated:
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)  # Создаём или получаем корзину
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        session_key = request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_key=session_key)  # Корзина для анонимных

    #  Получаем товары из корзины
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})


def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    # Удаляем товар из корзины
    cart_item.delete()

    return redirect('cart_view')


def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        CartItem.objects.filter(cart=cart).delete()
    return redirect('cart_view')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Выполняем вход
            messages.success(request, 'Вы успешно зарегистрировались! Теперь вы можете войти.')
            return redirect('product_list')

        else:
            messages.error(request, 'Ошибка регистрации. Проверьте введённые данные.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/signup.html', {'form': form})


# ---------


# @csrf_exempt
def place_order(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

    recipient_name = request.POST.get("recipient_name")
    address = request.POST.get("address")
    phone_number = request.POST.get("phone_number")
    comment = request.POST.get("comment", "")

    # 🔑 Добавляем новые поля для типа заказа и филиала
    order_type = request.POST.get("order_type")
    branch = request.POST.get("branch") if order_type == "preorder" else None

    if not recipient_name or not address or not phone_number:
        return JsonResponse({"success": False, "error": "Заполните все поля!"}, status=400)

    # Получаем корзину
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        email = user.email
        username = user.username
    else:
        user = None
        if not request.session.session_key:
            request.session.create()
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
        email = "guest@example.com"
        username = "Guest"

    if not cart:
        return JsonResponse({"success": False, "error": "Корзина не найдена"}, status=400)

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return JsonResponse({"success": False, "error": "Корзина пуста!"}, status=400)
    try:
    # Создаём заказ
        order = Order.objects.create(
            user=user,
            recipient_name=recipient_name,
            address=address,
            phone_number=phone_number,
            email=email,
        )

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

    total_price = 0
    order_summary = []

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        total_price += item.product.price * item.quantity
        order_summary.append(f"{item.product.name} x {item.quantity} = {item.product.price * item.quantity} So'm")

    cart_items.delete()
    cart.delete()

    from django.conf import settings
    import requests

    # Отправка в Telegram (оставляем как есть)
    message = (
            f"📦 New ZAKAZ\n"
            f"👤 Buyurtmachi: {username}\n"
            f"📧 Email: {email}\n\n"

            f"📋 Ma'lumotlar:\n"
            f"👤 Ismi: {recipient_name}\n"
            f"📍 Manzil: {address}\n"
            f"📱 Tel: {phone_number}\n\n"
            f"💬 Istaklari (comment): {comment if comment else 'No comment'}\n\n"

            f"🛒 Mahsulotlar:\n" + "\n".join(order_summary) +
            f"\n\n💰 Umumiy hisob: {total_price:.2f} So'm"
    )

    # Отправляем каждому ID из .env
    for chat_id in settings.CHAT_IDS:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}

        try:
            requests.post(url, json=payload)
        except Exception as e:
            print("Telegram error:", e)
    # send_telegram_message(message)

    return JsonResponse({"success": True, "redirect_url": "/order_success/"})


# @csrf_exempt
# def place_order(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)
#
#     recipient_name = request.POST.get("recipient_name")
#     address = request.POST.get("address")
#     phone_number = request.POST.get("phone_number")
#
#     if not recipient_name or not address or not phone_number:
#         return JsonResponse({"success": False, "error": "Заполните все поля!"}, status=400)
#
#     # Получаем корзину
#     if request.user.is_authenticated:
#         user = request.user
#         cart = Cart.objects.filter(user=user).first()
#         email = user.email
#         username = user.username
#     else:
#         user = None
#         if not request.session.session_key:
#             request.session.create()
#         cart = Cart.objects.filter(session_key=request.session.session_key).first()
#         email = "guest@example.com"
#         username = "Guest"
#
#     if not cart:
#         return JsonResponse({"success": False, "error": "Корзина не найдена"}, status=400)
#
#     cart_items = CartItem.objects.filter(cart=cart)
#     if not cart_items.exists():
#         return JsonResponse({"success": False, "error": "Корзина пуста!"}, status=400)
#
#     # Создаём заказ
#     order = Order.objects.create(
#         user=user,
#         recipient_name=recipient_name,
#         address=address,
#         phone_number=phone_number,
#         email=email
#     )
#
#     total_price = 0
#     order_summary = []
#
#     for item in cart_items:
#         OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
#         total_price += item.product.price * item.quantity
#         order_summary.append(f"{item.product.name} x {item.quantity} = {item.product.price * item.quantity} ₴")
#
#     cart_items.delete()
#
#     message = (
#         f"📦 New ZAKAZ\n"
#         f"👤 Buyurtmachi: {username}\n"
#         f"📧 Email: {email}\n\n"
#         f"📋 Ma'lumotlar:\n"
#         f"👤 Ismi: {recipient_name}\n"
#         f"📍 Manzil: {address}\n"
#         f"📱 Tel: {phone_number}\n\n"
#         f"🛒 Mahsulotlar:\n" + "\n".join(order_summary) +
#         f"\n\n💰 Umumiy hisob: {total_price:.2f} ₴"
#     )
#
#     send_telegram_message(message)
#
#     return JsonResponse({"success": True, "redirect_url": "/order_success/"})

# -------
# # @login_required
# @csrf_exempt
# def place_order(request):
#     if request.method == "POST":
#         recipient_name = request.POST.get("recipient_name")
#         address = request.POST.get("address")
#         phone_number = request.POST.get("phone_number")
#
#         if not recipient_name or not address or not phone_number:
#             return JsonResponse({"success": False, "error": "Заполните все поля!"})
#         user = request.user if request.user.is_authenticated else None
#         user = request.user
#         cart = Cart.objects.get(user=request.user)
#         cart_items = CartItem.objects.filter(cart=cart)
#
#         if not cart_items.exists():
#             return JsonResponse({"success": False, "error": "Корзина пуста!"}, status=400)
#
#         order = Order.objects.create(
#             user=request.user,
#             recipient_name=recipient_name,
#             address=address,
#             phone_number=phone_number,
#             email=user.email
#         )
#
#         order_summary = []
#         total_price = 0
#         total_quantity = 0  # ✅ Добавляем переменную для общего количества
#
#         for item in cart_items:
#             OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
#             total_price += item.product.price * item.quantity
#             total_quantity += item.quantity  # 🔥 Считаем общее количество товаров
#             order_summary.append(f"{item.product.name} x {item.quantity} = {item.product.price * item.quantity} ₴")
#
#         cart_items.delete()  # ✅ Очищаем корзину после заказа
#
#         message = (
#             f"📦New ZAKAZ \n"
#             f"🌐{user.username}-Buyurtma beruvchi!\n"
#             f"📧 E-mail : {user.email}\n\n"
#             f"📋Buyurtma danniylari! \n\n"
#             f"👤 Ismi: {recipient_name} \n"
#             f"📍 Adresi: {address}\n"
#             f"📱 Tel: {phone_number}\n\n"
#             # f"⏳ Время заказа: {localtime(order.created_at).strftime('%d.%m.%Y %H:%M')}\n\n"
#             f"🛒 Mahsulot:\n\n" + "\n".join(order_summary) + f"\n\n💰 Umumiy hisob: {total_price:.2f}₴"
#         )
#         send_telegram_message(message)
#
#         # ✅ Возвращаем **общее количество товаров**, вместо `cart_item.quantity`
#         # return redirect("cart_view")
#         return JsonResponse({"success": True, "redirect_url": "/order_success/"})
#
#     return render(request, "store/place_order.html")

def order_success(request):
    return render(request, 'store/order_success.html')


def payment_view(request):
    pass  # Заглушка, пока функционал не нужен
