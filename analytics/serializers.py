from rest_framework import serializers
from .models import SiteAnalytics

class SiteAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteAnalytics
        exclude = ['id']
