from rest_framework import serializers
from .models import AccountReview,ItemReview,BaseReview
from rest_framework.exceptions import ValidationError
from pendingrequests.models import PendingRequest

class AccountReviewSerializerIncoming(serializers.ModelSerializer):
    offer = serializers.PrimaryKeyRelatedField(
        queryset=PendingRequest.objects.none(),  # will be set dynamically
        error_messages={
            "does_not_exist": "This offer does not exist or is not available.",
            "incorrect_type": "Invalid offer ID.",
            "required": "An offer is required to leave a review.",
        }
    )
    class Meta:
        model = AccountReview
        fields = ["rating","comment","offer"]
        extra_kwargs = {
            "rating": {"required": True},
            "offer": {"required": True},
        }

        #the get_fields practically says what objects are to pass through the validation. SO here, we can filter out all the ones where the user is not th buyer.
    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            fields["offer"].queryset = PendingRequest.objects.filter(
                buyer=request.user
            )
        else:
            fields["offer"].queryset = PendingRequest.objects.none()

        return fields

    #NOTE validate() -> object level, validate_<field> field level
    def validate(self, attrs):
        offer = attrs["offer"]

        if hasattr(offer, 'seller_reviewed'):
            raise serializers.ValidationError({
                "offer": "This offer already has a review."
            })
        
        if(offer.response is not True):
           raise ValidationError({"non_valid_offer": "Only an accepted offer may lead to review"})

        user = self.context["request"].user

        if(offer.buyer != user):
            raise ValidationError({"bad_actor":"Only the offer initiator may leave a review"})
        
        return super().validate(attrs)

    def create(self,validated_data):
        offer=validated_data["offer"]
        validated_data["seller"] = offer.item.seller
        return super().create(validated_data)

class ItemReviewSerializerIncoming(serializers.ModelSerializer):

    #this is how you set custome error messages.
    offer = serializers.PrimaryKeyRelatedField(
        queryset=PendingRequest.objects.none(),  # will be set dynamically
        error_messages={
            "does_not_exist": "This offer does not exist or is not available.",
            "incorrect_type": "Invalid offer ID.",
            "required": "An offer is required to leave a review.",
        }
    )
    class Meta:
        model = ItemReview
        fields = ["rating","comment","offer"]
        extra_kwargs = {
            "rating": {"required": True},
            "offer": {"required": True},
        }

    #the get_fields practically says what objects are to pass through the validation. SO here, we can filter out all the ones where the user is not th buyer.
    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            fields["offer"].queryset = PendingRequest.objects.filter(
                buyer=request.user
            )
        else:
            fields["offer"].queryset = PendingRequest.objects.none()

        return fields
    
    def validate(self, attrs):
        offer = attrs["offer"]

        if hasattr(offer, 'item_reviewed'):
            raise serializers.ValidationError({
                "offer": "This offer already has a review."
            })
        
        if(offer.response is not True):
           raise ValidationError({
    "non_valid_offer": "Only an accepted offer may lead to review"
})

        user = self.context["request"].user

        if(offer.buyer != user):
            raise ValidationError({"bad_actor":"Only the offer initiator may leave a review"})
        
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