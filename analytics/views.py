from .models import SiteAnalytics
from .serializers import SiteAnalyticsSerializer
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from user.permissions import IsAdmin
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer

class SiteAnalyticsView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(responses={200: inline_serializer(
        name="SiteAnalyticsResponse", fields={
            "requested_at": serializers.DateTimeField(),
            "last_update": serializers.DateTimeField(allow_null=True),
            "data": SiteAnalyticsSerializer(many=True)
        }
    )})
    def get(self, request, *args, **kwargs):
        newest = SiteAnalytics.objects.order_by("created_at").reverse()[:48]
        return Response({
            "requested_at": timezone.now(),
            "last_update": newest[0].created_at if newest else None,
            "data": SiteAnalyticsSerializer(newest, many=True).data[::-1]
        })
