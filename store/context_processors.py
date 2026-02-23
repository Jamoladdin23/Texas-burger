from .models import Category
from .models import Cart


def categories_processor(request):
    return {
        'all_categories': Category.objects.all()
    }

def cart_data(request):
    cart = None
    cart_count = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()

    if cart:
        # cart_count = cart.items.count()
        cart_count = sum(item.quantity for item in cart.items.all())

    return {
        "cart_count": cart_count
    }