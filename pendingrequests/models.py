from django.db import models
from django.utils import timezone
from user.models import User
from item.models import Item

class PendingRequest(models.Model):
     buyer      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
     item       = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='interested_buyers')
     created_at = models.DateTimeField(auto_now_add=True)
     message    = models.TextField(blank=True, null=True)
     quantity   = models.PositiveIntegerField(default=1)

     answered_at    = models.DateTimeField(null=True, blank=True)
     response= models.BooleanField(default=None,null=True) # true=accepted false=rejected null=unanswered

     def mark_answered(self):
         self.is_answered=True
         self.answered_at=timezone.now()
         self.now()

     def __str__(self): 
        return f"{self.buyer.username} is interested in {self.item.title}"
