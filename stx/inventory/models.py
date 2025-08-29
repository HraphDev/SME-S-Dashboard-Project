from django.utils import timezone
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def quantity(self):
        """Calcule le stock en fonction des mouvements (Entrées - Sorties)."""
        entries = self.movements.filter(movement_type='in').aggregate(total=models.Sum('quantity'))['total'] or 0
        exits = self.movements.filter(movement_type='out').aggregate(total=models.Sum('quantity'))['total'] or 0
        return entries - exits

    def __str__(self):
        return self.name


class ProductMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Entrée'),
        ('out', 'Sortie'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity})"
