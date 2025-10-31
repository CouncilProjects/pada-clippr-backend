from django.db import models
from user.models import User
from item.models import Item
from django.utils import timezone

class PendingRequest(models.Model):
     buyer=models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
     item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='interested_buyers')
     created_at = models.DateTimeField(auto_now_add=True)
     message = models.TextField(blank=True, null=True)

     answered_at=models.DateTimeField(null=True, blank=True)
     is_answered =models.BooleanField(default=False)


     def mark_answered(self):
         self.is_answered=True
         self.answered_at=timezone.now()
         self.now()

     def __str__(self): 
        return f"{self.buyer.username} is interested in {self.item.title}"