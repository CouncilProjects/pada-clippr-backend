from django.db import models
from user.models import User
from item.models import Item
from pendingrequests.models import PendingRequest
from django.core.validators import MinValueValidator, MaxValueValidator

class BaseReview(models.Model):
     rating = models.DecimalField(max_digits=2,decimal_places=1,validators=[MinValueValidator(0),MaxValueValidator(5)])
     comment = models.TextField(blank=True, null=True)
     created_at = models.DateTimeField(auto_now_add=True)
     class Meta:
          abstract=True


class AccountReview(BaseReview):
     offer=models.OneToOneField(PendingRequest,null=True,blank=True,on_delete=models.SET_NULL,related_name='seller_reviewed')
     seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')

class ItemReview(BaseReview):
      offer=models.OneToOneField(PendingRequest,null=True,blank=True,on_delete=models.SET_NULL,related_name='item_reviewed')
      item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
