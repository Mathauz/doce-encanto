from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Product(models.Model):
    name = models.CharField("nome", max_length=120)
    description = models.TextField("descrição")
    price = models.DecimalField(
        "preço", max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    image = models.CharField("imagem estática", max_length=200, blank=True)
    active = models.BooleanField("ativo", default=True)
    featured = models.BooleanField("destaque", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        constraints = [models.CheckConstraint(condition=Q(price__gt=0), name="product_price_gt_zero")]

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", "Recebido"
        PREPARING = "preparing", "Em preparo"
        OUT_FOR_DELIVERY = "out_for_delivery", "Saiu para entrega"
        COMPLETED = "completed", "Concluído"
        CANCELLED = "cancelled", "Cancelado"

    class PaymentMethod(models.TextChoices):
        PIX = "pix_demo", "Pix simulado"
        CARD = "card_on_delivery", "Cartão na entrega"
        CASH = "cash", "Dinheiro"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    recipient_name = models.CharField("nome de quem recebe", max_length=120)
    street = models.CharField("rua", max_length=160)
    number = models.CharField("número", max_length=20)
    complement = models.CharField("complemento", max_length=80, blank=True)
    district = models.CharField("bairro", max_length=100)
    city = models.CharField("cidade", max_length=100)
    state = models.CharField("UF", max_length=2)
    postal_code = models.CharField("CEP", max_length=9)
    payment_method = models.CharField("pagamento", max_length=24, choices=PaymentMethod.choices)
    status = models.CharField("status", max_length=24, choices=Status.choices, default=Status.RECEIVED)
    notes = models.TextField("observações", blank=True)
    total = models.DecimalField("total", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido #{self.pk}"

    @property
    def full_address(self):
        complement = f", {self.complement}" if self.complement else ""
        return f"{self.street}, {self.number}{complement} - {self.district}, {self.city}/{self.state} - {self.postal_code}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField("produto", max_length=120)
    unit_price = models.DecimalField("preço unitário", max_digits=8, decimal_places=2)
    quantity = models.PositiveSmallIntegerField("quantidade")

    class Meta:
        verbose_name = "item do pedido"
        verbose_name_plural = "itens do pedido"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

