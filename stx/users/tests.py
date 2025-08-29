from django.test import TestCase
from .models import Category, Product, ProductMovement

class ProductTestCase(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Test Cat")
        self.product = Product.objects.create(name="Test Product", category=self.cat, quantity=5, price=10.0)

    def test_is_low_stock(self):
        self.product.quantity = 2
        self.assertTrue(self.product.is_low_stock())

    def test_stock_out_movement(self):
        ProductMovement.objects.create(product=self.product, movement_type="out", quantity=2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)
