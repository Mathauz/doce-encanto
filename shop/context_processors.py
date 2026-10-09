from .cart import Cart


def cart_summary(request):
    cart = Cart(request.session)
    return {"cart_count": cart.count, "cart_total": cart.get_total()}

