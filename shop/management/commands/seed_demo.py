import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shop.models import Product


PRODUCTS = [
    {"name": "Brigadeiro intenso", "description": "Massa de chocolate, brigadeiro cremoso e granulado belga.", "price": "12.50", "image": "images/brigadeiro-intenso.png", "featured": True},
    {"name": "Morango delicado", "description": "Massa de baunilha, creme de morango e fruta fresca.", "price": "11.90", "image": "images/morango-delicado.png", "featured": True},
    {"name": "Baunilha com caramelo", "description": "Baunilha macia, caramelo artesanal e crocante dourado.", "price": "12.90", "image": "images/baunilha-caramelo.png", "featured": True},
    {"name": "Chocolate clássico", "description": "Chocolate intenso com cobertura cremosa e acabamento artesanal.", "price": "10.90", "image": "images/brigadeiro-intenso.png", "featured": False},
    {"name": "Nuvem de morango", "description": "Baunilha leve com creme rosado de morango.", "price": "10.50", "image": "images/morango-delicado.png", "featured": False},
    {"name": "Doce de caramelo", "description": "Cupcake amanteigado com cobertura de caramelo.", "price": "11.50", "image": "images/baunilha-caramelo.png", "featured": False},
]


class Command(BaseCommand):
    help = "Cria ou atualiza dados demonstrativos da Doce Encanto."

    def handle(self, *args, **options):
        for data in PRODUCTS:
            Product.objects.update_or_create(name=data["name"], defaults={**data, "active": True})
        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        if username and password:
            user, _ = get_user_model().objects.get_or_create(username=username)
            user.email = os.environ.get("ADMIN_EMAIL", "")
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
        if options.get("verbosity", 1):
            self.stdout.write(self.style.SUCCESS("Catálogo demonstrativo atualizado."))

