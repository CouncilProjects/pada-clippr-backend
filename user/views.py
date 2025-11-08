from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import UserRegisterSerializer

User = get_user_model()

# username, password, email, firstname, lastname
class Register(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        return Response(serializer.errors, status=400)

class Login(APIView):
    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = Response()
        response.set_cookie(
            key='refresh_token',
            value=serializer.validated_data['refresh'],
            path=reverse('user_refresh'),
            max_age=60 * 60 * 24 * 7, # One Week
            samesite='None',
            httponly=True,
            secure=True,
        )

        response.data = {
            'token': serializer.validated_data['access'],
            'username': serializer.user.username,
            'role': serializer.user.get_role_name(),
        }

        return response

class Refresh(APIView):
    def get(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token missing."}, status=400)

        request.data['refresh'] = request.COOKIES.get('refresh_token')
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(refresh_token)
            user = User.objects.get(id=token['user_id'])
        except (TokenError, InvalidToken, User.DoesNotExist) as e:
            return Response({"detail": "Invalid token."}, status=401)

        return Response({
            "token": serializer.validated_data['access'],
            "username": user.username,
            "role": user.get_role_name(),
        })
