from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import generics
from .permissions import IsAdmin
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserRegisterSerializer,AvatarUploadSerializer,UserSerializer,UserBasicSerializer

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

class Logout(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie(
            key='refresh_token',
            path=reverse('user_refresh'),
        )

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


class AvatarUpload(APIView):
    parser_classes=[MultiPartParser,FormParser]
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer = AvatarUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=request.user)

        return Response(
            {'message': 'Avatar uploaded successfully'},
            status=status.HTTP_201_CREATED
        )
    def get(self, request):

        serializer = UserSerializer(request.user)  # Pass instance to serialize
        
        return Response(
            {'userAvatar': serializer.data['avatar']},
            status=status.HTTP_200_OK
        )
    def delete(self, request):

        request.user.avatar.all().delete()

        
        return Response(
            {'userAvatar': []},
            status=status.HTTP_200_OK
        )
    
class UserBasicListView(generics.ListAPIView):
    queryset = User.objects.all().exclude(is_verified_seller=1)
    serializer_class = UserBasicSerializer

class UserViewSet(ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    @action(detail=False, methods=['get'])
    def unverified(self, request):
        users = User.objects.all().exclude(is_verified_seller=1).exclude(is_superuser=1)
        serializer = UserBasicSerializer(users,many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'],permission_classes=[IsAdmin])
    def verify(self, request,pk=None):
        user = self.get_object()
        user.is_verified_seller = 1
        user.save()
        
        return Response({"message": "User marked as verified"},status=status.HTTP_200_OK)