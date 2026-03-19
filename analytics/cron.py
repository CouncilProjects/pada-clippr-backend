def collect_site_analytics():
    from user.models import User
    from item.models import Item
    from .models import SiteAnalytics
    from django.db.models import Q
    from django.utils import timezone
    from datetime import timedelta

    member_count = User.objects.filter(Q(is_verified_seller=False) & Q(is_superuser=False) & Q(is_staff=False)).count()
    seller_count = User.objects.filter(Q(is_verified_seller=True) & Q(is_superuser=False) & Q(is_staff=False)).count()
    admin_count = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True)).count()

    member_items_count = Item.objects.filter(seller__is_verified_seller=False).count()
    seller_items_count = Item.objects.filter(seller__is_verified_seller=True).count()

    member_used_tags_count = Item.objects.filter(seller__is_verified_seller=False).values('tags').count()
    seller_used_tags_count = Item.objects.filter(seller__is_verified_seller=True).values('tags').count()
    member_distinct_tags_count = Item.objects.filter(seller__is_verified_seller=False).values('tags').distinct().count()
    seller_distinct_tags_count = Item.objects.filter(seller__is_verified_seller=True).values('tags').distinct().count()

    SiteAnalytics.objects.create(
        member_count=member_count,
        seller_count=seller_count,
        admin_count=admin_count,
        member_items_count=member_items_count,
        seller_items_count=seller_items_count,
        member_distinct_tags_count=member_distinct_tags_count,
        seller_distinct_tags_count=seller_distinct_tags_count,
        member_used_tags_count=member_used_tags_count,
        seller_used_tags_count=seller_used_tags_count
    )

    cutoff = timezone.now() - timedelta(days=30)
    SiteAnalytics.objects.filter(created_at__lt=cutoff).delete()

def collect_seller_analytics():
    from user.models import User
    from item.models import Item
    from pendingrequests.models import PendingRequest
    from .models import SellerAnalytics
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta

    for seller in User.objects.filter(is_verified_seller=True):
        items_count = Item.objects.filter(seller=seller).count()
        used_tags_count = Item.objects.filter(seller=seller).values('tags').count()
        distinct_tags_count = Item.objects.filter(seller=seller).values('tags').distinct().count()

        accepted_request_count = PendingRequest.objects.filter(item__seller=seller, response=True).count()
        rejected_request_count = PendingRequest.objects.filter(item__seller=seller, response=False).count()
        total_views = Item.objects.filter(seller=seller).aggregate(sum=Sum('views'))['sum'] or 0

        SellerAnalytics.objects.create(
            seller=seller,
            items_count=items_count,
            used_tags_count=used_tags_count,
            distinct_tags_count=distinct_tags_count,
            accepted_request_count=accepted_request_count,
            rejected_request_count=rejected_request_count,
            total_views=total_views
        )

    cutoff = timezone.now() - timedelta(days=30)
    SellerAnalytics.objects.filter(created_at__lt=cutoff).delete()
