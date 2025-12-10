from rest_framework import serializers
from .models import AccountReview,ItemReview,BaseReview
from rest_framework.exceptions import ValidationError

class AccountReviewSerializerIncoming(serializers.ModelSerializer):
    class Meta:
        model = AccountReview
        fields = ["rating","comment","offer"]
        extra_kwargs = {
            "rating": {"required": True},
            "offer": {"required": True},
        }

    #NOTE validate() -> object level, validate_<field> field level
    def validate(self, attrs):
        offer = attrs["offer"]
        
        if(offer.response is not True):
           raise ValidationError("Only an accepted offer may lead to review")

        user = self.context["request"].user

        if(offer.buyer != user):
            raise ValidationError("Only the offer initiator may leave a review")
        
        return super().validate(attrs)

    def create(self,validated_data):
        offer=validated_data["offer"]
        validated_data["seller"] = offer.seller
        return super().create(validated_data)

class ItemReviewSerializerIncoming(serializers.ModelSerializer):
    class Meta:
        model = ItemReview
        fields = ["rating","comment","offer"]
        extra_kwargs = {
            "rating": {"required": True},
            "offer": {"required": True},
        }
    def validate(self, attrs):
        offer = attrs["offer"]
        
        if(offer.response is not True):
           raise ValidationError("Only an accepted offer may lead to review")

        user = self.context["request"].user

        if(offer.buyer != user):
            raise ValidationError("Only the offer initiator may leave a review")
        
        return super().validate(attrs)
    def create(self,validated_data):
        offer=validated_data["offer"]
        validated_data["item"] = offer.item
        return super().create(validated_data)

class ItemReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model= ItemReview
        exclude=['offer']

class AccountReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model= AccountReview
        exclude=['offer']