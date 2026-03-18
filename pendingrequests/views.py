from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import PendingRequest
from .serializers import PendingRequestSerializer, PendingRequestCreateSerializer


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
            status="pending"
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
        offers = PendingRequest.objects.filter(buyer=request.user, status='pending').select_related('item__seller').order_by('-created_at')
        return Response(PendingRequestSerializer(offers, many=True).data)
