from django.db import models

# Menu Item Model
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)

    def __str__(self):
        return self.name


# Order Model
class Order(models.Model):
    customer_name = models.CharField(max_length=100, default='Guest')
    phone = models.CharField(max_length=15, null=True)
    email = models.EmailField(blank=True)
    address = models.TextField()
    notes = models.TextField(blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


# Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"{self.quantity} x {self.item.name} (Order #{self.order.id})"



