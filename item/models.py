from django.db import models
from user.models import User

class Item(models.Model):
      seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
      title = models.CharField(max_length=200)
      description = models.TextField()
      price = models.DecimalField(max_digits=10,decimal_places=2)
      stock = models.PositiveIntegerField(default=1)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      def __str__(self):
           return f"{self.title} by {self.seller.username}" 
