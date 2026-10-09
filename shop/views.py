from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, QuantityForm, RegistrationForm
from .models import Order, OrderItem, Product


def home(request):
    featured = list(Product.objects.filter(active=True, featured=True).order_by("created_at")[:3])
    if len(featured) < 3:
        featured = list(Product.objects.filter(active=True).order_by("created_at")[:3])
    return render(request, "shop/home.html", {"products": featured})


def product_list(request):
    return render(request, "shop/product_list.html", {"products": Product.objects.filter(active=True)})


def register(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Conta criada. Bem-vindo à Doce Encanto!")
        return redirect("shop:home")
    return render(request, "registration/register.html", {"form": form})


def cart_detail(request):
    return render(request, "shop/cart.html", {"cart": Cart(request.session)})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, active=True)
    form = QuantityForm(request.POST)
    if form.is_valid():
        Cart(request.session).add(product, form.cleaned_data["quantity"])
        messages.success(request, f"{product.name} foi adicionado ao carrinho.")
    else:
        messages.error(request, "Escolha uma quantidade entre 1 e 20.")
    return redirect(request.POST.get("next") or "shop:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id, active=True)
    form = QuantityForm(request.POST)
    if form.is_valid():
        Cart(request.session).update(product, form.cleaned_data["quantity"])
    else:
        messages.error(request, "Escolha uma quantidade entre 1 e 20.")
    return redirect("shop:cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Cart(request.session).remove(product)
    messages.info(request, f"{product.name} foi removido do carrinho.")
    return redirect("shop:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request.session)
    items = list(cart)
    form = CheckoutForm(request.POST or None)
    if not items:
        return render(request, "shop/checkout.html", {"form": form, "cart": cart, "cart_error": "Seu carrinho está vazio."})
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked = {
                product.pk: product
                for product in Product.objects.select_for_update().filter(
                    pk__in=[item["product"].pk for item in items], active=True
                )
            }
            if len(locked) != len(items):
                messages.error(request, "Um produto deixou de estar disponível. Revise o carrinho.")
                return render(request, "shop/checkout.html", {"form": form, "cart": cart})
            order = form.save(commit=False)
            order.user = request.user
            order.total = sum(locked[item["product"].pk].price * item["quantity"] for item in items)
            order.save()
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=locked[item["product"].pk],
                    product_name=locked[item["product"].pk].name,
                    unit_price=locked[item["product"].pk].price,
                    quantity=item["quantity"],
                )
                for item in items
            ])
        cart.clear()
        messages.success(request, f"Pedido #{order.pk} recebido com sucesso.")
        return redirect("shop:order_detail", pk=order.pk)
    return render(request, "shop/checkout.html", {"form": form, "cart": cart})


@login_required
def order_list(request):
    return render(request, "shop/order_list.html", {"orders": request.user.orders.prefetch_related("items")})


@login_required
def order_detail(request, pk):
    try:
        order = request.user.orders.prefetch_related("items").get(pk=pk)
    except Order.DoesNotExist as exc:
        raise Http404("Pedido não encontrado") from exc
    return render(request, "shop/order_detail.html", {"order": order})
