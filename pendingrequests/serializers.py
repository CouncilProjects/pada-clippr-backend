from rest_framework import serializers
from .models import PendingRequest

class PendingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingRequest
        fields = '__all__'
