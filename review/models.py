from django.db import models
from user.models import User
from item.models import Item
from pendingrequests.models import PendingRequest

class BaseReview(models.Model):
     rating = models.PositiveSmallIntegerField()
     comment = models.TextField(blank=True, null=True)
     created_at = models.DateTimeField(auto_now_add=True)
     class Meta:
          abstract=True

class AccountReview(BaseReview):
     offer=models.OneToOneField(PendingRequest,on_delete=models.CASCADE,related_name='seller_reviewed')
     seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')

class ItemReview(BaseReview):
      offer=models.OneToOneField(PendingRequest,on_delete=models.CASCADE,related_name='item_review')
      item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
