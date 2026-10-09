from decimal import Decimal

from .models import Product


class Cart:
    session_key = "cart"

    def __init__(self, session):
        self.session = session
        self.data = session.get(self.session_key, {})

    def _save(self):
        self.session[self.session_key] = self.data
        self.session.modified = True
        if hasattr(self.session, "save"):
            self.session.save()

    def add(self, product, quantity=1, replace=False):
        key = str(product.pk)
        current = 0 if replace else int(self.data.get(key, 0))
        self.data[key] = min(20, max(1, current + int(quantity)))
        self._save()

    def update(self, product, quantity):
        quantity = int(quantity)
        if quantity <= 0:
            self.remove(product)
            return
        self.data[str(product.pk)] = min(20, quantity)
        self._save()

    def remove(self, product):
        self.data.pop(str(product.pk), None)
        self._save()

    def clear(self):
        self.data = {}
        self._save()

    def __iter__(self):
        ids = list(self.data.keys())
        products = {str(p.pk): p for p in Product.objects.filter(pk__in=ids, active=True)}
        changed = False
        for key in ids:
            product = products.get(key)
            if product is None:
                self.data.pop(key, None)
                changed = True
                continue
            quantity = min(20, max(1, int(self.data[key])))
            yield {
                "product": product,
                "quantity": quantity,
                "unit_price": product.price,
                "subtotal": product.price * quantity,
            }
        if changed:
            self._save()

    @property
    def count(self):
        return sum(item["quantity"] for item in self)

    def get_total(self):
        return sum((item["subtotal"] for item in self), Decimal("0.00"))

    def __len__(self):
        return self.count
