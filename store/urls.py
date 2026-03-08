from django.urls import path
from . import views
from .views import CustomLoginView, signup
from django.contrib.auth import views as auth_views  # Импорт встроенных представлений Django

urlpatterns = [
    # path('', views.product_list, name='product_list'),
    path('', views.home, name='main'),
    path('menu/', views.product_list, name='product_list'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('product_list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path("product/options/<int:product_id>/", views.get_product_options, name="product_options"),

    path('cart/add/product/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('signup/', signup, name='signup'),
    path('place_order/', views.place_order, name='place_order'),

    path('order_success/', views.order_success, name='order_success'),
    path('payment/', views.payment_view, name='payment_view'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),

    # path('place_order/<int:product_id>/', views.place_order_product, name='place_order_product'),
    path('place_order/', views.place_order, name='place_order'),

    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]
