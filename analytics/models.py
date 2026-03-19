from django.db import models
from user.models import User

class SiteAnalytics(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    member_count = models.IntegerField(default=0)
    seller_count = models.IntegerField(default=0)
    admin_count = models.IntegerField(default=0)

    member_items_count = models.IntegerField(default=0)
    seller_items_count = models.IntegerField(default=0)
    member_used_tags_count = models.IntegerField(default=0)
    seller_used_tags_count = models.IntegerField(default=0)
    member_distinct_tags_count = models.IntegerField(default=0)
    seller_distinct_tags_count = models.IntegerField(default=0)

class SellerAnalytics(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE,
        limit_choices_to={"is_verified_seller": True})

    items_count = models.IntegerField(default=0)
    used_tags_count = models.IntegerField(default=0)
    distinct_tags_count = models.IntegerField(default=0)

    accepted_request_count = models.IntegerField(default=0)
    rejected_request_count = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)
