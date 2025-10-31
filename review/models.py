from django.db import models
from user.models import User
from item.models import Item

class Review(models.Model):
     seller= models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
     buyer=models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
     item=models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
     rating=models.PositiveSmallIntegerField()
     comment=models.TextField(blank=True, null=True)
     created_at=models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return f"Review by {self.buyer.username} for {self.seller.username} ({self.rating}/5)"
