from django.urls import path
from . import views

urlpatterns = [
   path('', views.menu, name='menu'),
   path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
   path('cart/', views.view_cart, name='view_cart'),
   path('checkout/', views.checkout, name='checkout'),
   path('order-success/<int:order_id>/', views.order_success, name='order_success'),
   path('pay-order/<int:order_id>/', views.lipa_na_mpesa_online, name='lipa_na_mpesa_online'),
   path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
   path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
   ]
