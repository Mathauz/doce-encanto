from django.core.management import call_command
from django.test import TestCase

from shop.models import Product


class SeedDemoTests(TestCase):
    def test_seed_demo_is_idempotent_and_creates_expected_catalog(self):
        call_command("seed_demo", verbosity=0)
        call_command("seed_demo", verbosity=0)
        self.assertEqual(Product.objects.count(), 6)
        self.assertEqual(Product.objects.filter(featured=True).count(), 3)
        self.assertTrue(Product.objects.filter(name="Brigadeiro intenso", image="images/brigadeiro-intenso.png").exists())
