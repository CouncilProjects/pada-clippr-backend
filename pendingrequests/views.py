from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import PendingRequest
from .serializers import PendingRequestSerializer, PendingRequestCreateSerializer
from django.db.models import Exists, OuterRef
from review.models import AccountReview, ItemReview


class CreatePendingRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PendingRequestCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        item = serializer.validated_data["item_id"]

        if item.seller == request.user:
            return Response(
                {"detail": "You cannot request your own item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if PendingRequest.objects.filter(
            item=item,
            buyer=request.user,
            response__isnull=True
        ).exists():
            return Response(
                {"detail": "You already sent a request for this item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        pending_request = serializer.save()

        return Response(
            PendingRequestSerializer(pending_request).data,
            status=status.HTTP_201_CREATED
        )


class ListPendingRequests(APIView):
    """List pending requests for items owned by the user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        pending = PendingRequest.objects.filter(item__seller=request.user).order_by('-created_at')
        return Response(PendingRequestSerializer(pending, many=True).data)


class ListMyOffers(APIView):
    """List current outgoing offers made by the user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        offers = (
            PendingRequest.objects
            .filter(buyer=request.user)
            .exclude(response=False)
            .select_related('item__seller')
            .annotate(
                is_seller_reviewed=Exists(
                    AccountReview.objects.filter(offer_id=OuterRef('pk'))
                ),
                is_item_reviewed=Exists(
                    ItemReview.objects.filter(offer_id=OuterRef('pk'))
                ),
            )
            .order_by('-created_at')
        )
        return Response(PendingRequestSerializer(offers, many=True).data)

class HandlePendingRequest(APIView):
    """Accept or reject a pending request for an item owned by the user."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            pending_request = PendingRequest.objects.select_related('item__seller').get(pk=pk)
        except PendingRequest.DoesNotExist:
            return Response({"detail": "Pending request not found."}, status=status.HTTP_404_NOT_FOUND)

        if pending_request.item.seller != request.user:
            return Response({"detail": "You do not have permission to respond to this request."}, status=status.HTTP_403_FORBIDDEN)

        response = request.data.get('response')
        message = request.data.get('message', '')

        if response not in [True, False]:
            return Response({"detail": "Response must be true (accept) or false (reject)."}, status=status.HTTP_400_BAD_REQUEST)

        pending_request.mark_answered(response=response, message=message)

        return Response(PendingRequestSerializer(pending_request).data)
