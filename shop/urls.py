from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "shop"
urlpatterns = [
    path("", views.home, name="home"),
    path("produtos/", views.product_list, name="product_list"),
    path("conta/cadastro/", views.register, name="register"),
    path("conta/entrar/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("conta/sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("carrinho/", views.cart_detail, name="cart_detail"),
    path("carrinho/adicionar/<int:product_id>/", views.cart_add, name="cart_add"),
    path("carrinho/alterar/<int:product_id>/", views.cart_update, name="cart_update"),
    path("carrinho/remover/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("pedidos/", views.order_list, name="order_list"),
    path("pedidos/<int:pk>/", views.order_detail, name="order_detail"),
]
