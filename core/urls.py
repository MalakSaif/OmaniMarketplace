from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Brand & Product Pages
    path('brand/<int:brand_id>/', views.brand_profile, name='brand_profile'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart Functionality
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # User Authentication
    path('register/', views.register, name='register'),

    # Brand Dashboard
    path('brand/dashboard/', views.brand_dashboard, name='brand_dashboard'),
    path('brand/product/add/', views.add_product, name='add_product'),
    path('brand/product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('brand/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('brand/dashboard/orders/', views.brand_orders, name='brand_orders'),

    # User Dashboard
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('update_profile/', views.update_profile, name='update_profile'),
]
