from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from shop.cart import Cart
from shop.forms import CheckoutForm, RegistrationForm
from shop.models import Order, OrderItem, Product


class ProductModelTests(TestCase):
    def test_product_rejects_negative_price(self):
        product = Product(name="Inválido", description="Teste", price=Decimal("-1.00"))
        with self.assertRaises(Exception):
            product.full_clean()

    def test_only_active_products_appear_in_catalog(self):
        Product.objects.create(name="Ativo", description="A", price="10.00", active=True)
        Product.objects.create(name="Inativo", description="I", price="12.00", active=False)
        response = self.client.get(reverse("shop:product_list"))
        self.assertContains(response, "Ativo")
        self.assertNotContains(response, "Inativo")

    def test_home_preserves_featured_creation_order(self):
        for name in ["Brigadeiro intenso", "Morango delicado", "Baunilha com caramelo"]:
            Product.objects.create(name=name, description=name, price="10.00", featured=True)
        response = self.client.get(reverse("shop:home"))
        content = response.content.decode()
        self.assertLess(content.index("Brigadeiro intenso"), content.index("Morango delicado"))
        self.assertLess(content.index("Morango delicado"), content.index("Baunilha com caramelo"))


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Brigadeiro intenso", description="Chocolate", price="12.50", active=True
        )

    def test_cart_adds_and_recalculates_total_from_database_price(self):
        session = self.client.session
        cart = Cart(session)
        cart.add(self.product, quantity=2)
        self.product.price = Decimal("13.00")
        self.product.save()
        self.assertEqual(cart.get_total(), Decimal("26.00"))

    def test_cart_caps_quantity_at_twenty(self):
        cart = Cart(self.client.session)
        cart.add(self.product, quantity=21)
        self.assertEqual(cart.count, 20)

    def test_inactive_product_is_removed_from_cart(self):
        cart = Cart(self.client.session)
        cart.add(self.product, quantity=1)
        self.product.active = False
        self.product.save()
        self.assertEqual(list(cart), [])


class FormTests(TestCase):
    def test_registration_rejects_duplicate_email(self):
        get_user_model().objects.create_user(username="ana", email="ana@example.com", password="SenhaForte123")
        form = RegistrationForm(data={
            "username": "ana2", "email": "ana@example.com", "password1": "SenhaForte123!", "password2": "SenhaForte123!"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_checkout_requires_address_and_payment(self):
        form = CheckoutForm(data={"recipient_name": "Ana"})
        self.assertFalse(form.is_valid())
        for field in ["street", "number", "district", "city", "state", "postal_code", "payment_method"]:
            self.assertIn(field, form.errors)


class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="matheus", email="matheus@example.com", password="SenhaForte123!"
        )
        self.other = get_user_model().objects.create_user(
            username="outro", email="outro@example.com", password="SenhaForte123!"
        )
        self.product = Product.objects.create(
            name="Morango delicado", description="Morango", price="11.90", active=True
        )
        self.checkout_data = {
            "recipient_name": "Matheus Mattos",
            "street": "Rua das Flores",
            "number": "100",
            "complement": "Apto 1",
            "district": "Centro",
            "city": "São Paulo",
            "state": "SP",
            "postal_code": "01001-000",
            "payment_method": Order.PaymentMethod.PIX,
            "notes": "Sem alteração",
        }

    def test_checkout_requires_authentication(self):
        response = self.client.get(reverse("shop:checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("shop:login"), response.url)

    def test_checkout_rejects_empty_cart(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("shop:checkout"), self.checkout_data)
        self.assertEqual(Order.objects.count(), 0)
        self.assertContains(response, "Seu carrinho está vazio")

    def test_checkout_creates_order_items_and_clears_cart(self):
        self.client.force_login(self.user)
        session = self.client.session
        cart = Cart(session)
        cart.add(self.product, quantity=2)
        response = self.client.post(reverse("shop:checkout"), self.checkout_data)
        order = Order.objects.get()
        self.assertRedirects(response, reverse("shop:order_detail", args=[order.pk]))
        self.assertEqual(order.total, Decimal("23.80"))
        item = OrderItem.objects.get(order=order)
        self.assertEqual(item.product_name, "Morango delicado")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_checkout_does_not_create_partial_order_when_product_is_inactive(self):
        self.client.force_login(self.user)
        session = self.client.session
        cart = Cart(session)
        cart.add(self.product, quantity=1)
        self.product.active = False
        self.product.save()
        response = self.client.post(reverse("shop:checkout"), self.checkout_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_user_cannot_view_another_users_order(self):
        order = Order.objects.create(
            user=self.other, recipient_name="Outro", street="Rua B", number="2",
            district="Bairro", city="Cidade", state="SP", postal_code="01001-000",
            payment_method=Order.PaymentMethod.CASH, total="10.00"
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("shop:order_detail", args=[order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_order_history_lists_only_authenticated_users_orders(self):
        own = Order.objects.create(
            user=self.user, recipient_name="Matheus", street="Rua A", number="1",
            district="Centro", city="Cidade", state="SP", postal_code="01001-000",
            payment_method=Order.PaymentMethod.PIX, total="10.00"
        )
        other = Order.objects.create(
            user=self.other, recipient_name="Outro", street="Rua B", number="2",
            district="Bairro", city="Cidade", state="SP", postal_code="01001-000",
            payment_method=Order.PaymentMethod.CASH, total="12.00"
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("shop:order_list"))
        self.assertContains(response, f"Pedido #{own.pk}")
        self.assertNotContains(response, f"Pedido #{other.pk}")
