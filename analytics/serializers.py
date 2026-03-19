from rest_framework import serializers
from .models import SiteAnalytics, SellerAnalytics

class SiteAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteAnalytics
        exclude = ['id']

class SellerAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerAnalytics
        exclude = ['id']
