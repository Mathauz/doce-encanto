import decimal
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="nome")),
                ("description", models.TextField(verbose_name="descrição")),
                ("price", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))], verbose_name="preço")),
                ("image", models.CharField(blank=True, max_length=200, verbose_name="imagem estática")),
                ("active", models.BooleanField(default=True, verbose_name="ativo")),
                ("featured", models.BooleanField(default=False, verbose_name="destaque")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "produto", "verbose_name_plural": "produtos", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recipient_name", models.CharField(max_length=120, verbose_name="nome de quem recebe")),
                ("street", models.CharField(max_length=160, verbose_name="rua")),
                ("number", models.CharField(max_length=20, verbose_name="número")),
                ("complement", models.CharField(blank=True, max_length=80, verbose_name="complemento")),
                ("district", models.CharField(max_length=100, verbose_name="bairro")),
                ("city", models.CharField(max_length=100, verbose_name="cidade")),
                ("state", models.CharField(max_length=2, verbose_name="UF")),
                ("postal_code", models.CharField(max_length=9, verbose_name="CEP")),
                ("payment_method", models.CharField(choices=[("pix_demo", "Pix simulado"), ("card_on_delivery", "Cartão na entrega"), ("cash", "Dinheiro")], max_length=24, verbose_name="pagamento")),
                ("status", models.CharField(choices=[("received", "Recebido"), ("preparing", "Em preparo"), ("out_for_delivery", "Saiu para entrega"), ("completed", "Concluído"), ("cancelled", "Cancelado")], default="received", max_length=24, verbose_name="status")),
                ("notes", models.TextField(blank=True, verbose_name="observações")),
                ("total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10, verbose_name="total")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "pedido", "verbose_name_plural": "pedidos", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=120, verbose_name="produto")),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=8, verbose_name="preço unitário")),
                ("quantity", models.PositiveSmallIntegerField(verbose_name="quantidade")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="shop.order")),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="shop.product")),
            ],
            options={"verbose_name": "item do pedido", "verbose_name_plural": "itens do pedido"},
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(condition=models.Q(("price__gt", 0)), name="product_price_gt_zero"),
        ),
    ]
