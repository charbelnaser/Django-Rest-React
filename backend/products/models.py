from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(
        max_digits=4, decimal_places=2, help_text="VAT rate as percent, e.g. 20.00"
    )
    expiration_date = models.DateField(null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
