from django.db import models

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
