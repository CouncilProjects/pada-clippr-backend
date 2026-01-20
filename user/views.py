from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import generics

from user.models import SocialLink
from .permissions import IsAdmin, IsVerifiedSeller
from rest_framework.viewsets import GenericViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema

from .serializers import UserRegisterSerializer,AvatarUploadSerializer,UserSerializer,UserBasicSerializer,SocialLinkSerializer

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
            'id': serializer.user.id,
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
    
class DeleteAccount(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        User.delete(request.user)
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
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_400_BAD_REQUEST)

        request.data['refresh'] = request.COOKIES.get('refresh_token')
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(refresh_token)
            user = User.objects.get(id=token['user_id'])
        except (TokenError, InvalidToken, User.DoesNotExist) as e:
            return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            "token": serializer.validated_data['access'],
            'id': user.id,
            "username": user.username,
            "role": user.get_role_name(),
        }, status=status.HTTP_200_OK)


class AvatarUpload(GenericAPIView):
    parser_classes=[MultiPartParser,FormParser]
    permission_classes=[IsAuthenticated]
    serializer_class = AvatarUploadSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

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

class UserViewSet(GenericViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

    @action(detail=False, methods=['get'],
        url_path='by_username/(?P<username>[^/.]+)',
        permission_classes=[IsAuthenticated])
    def by_username(self, request, username=None):
        userId = get_object_or_404(User,username=username).id
        print(f"ViewSet of Users: Action socials: method:get called")

        return Response({"id": userId}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get unverified users",
        description="Retrieve the current list of unverified users.",
        responses={200: UserBasicSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def unverified(self, request):
        query = self.request.query_params.get('q',None)
        if(query==None):
            query=''
        usersFiltered = User.objects.filter(username__contains=query).exclude(Q(is_verified_seller=1) | Q(is_superuser=1))
        serializer = UserBasicSerializer(usersFiltered,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @extend_schema(
        summary="Verify a user",
        description="Verifies the chosen account",
        responses={200: {"message": "User marked as verified"}},
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def verify(self, request, pk=None):
        user = self.get_object()
        user.is_verified_seller = 1
        user.save()

        return Response(
            {"message": "User marked as verified"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def socials(self, request,pk=None):
        user = self.get_object()

        return Response({
            "socials": SocialLinkSerializer(user.social_links, many=True).data,
            "glint": user.is_verified_seller or user.is_superuser
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],permission_classes=[IsVerifiedSeller])
    def update_socials(self, request,pk=None):
        print(f"Here is requester : {request.user.id}")
        existingSocials = request.user.social_links.values_list('platform',flat=True) #use values_list to get certain fields, for multiple pls use .values
        print(f"Existing socials : {existingSocials}")
        for soc in request.data:
            if request.data[soc]=='':
                request.user.social_links.filter(platform=soc).delete()
            elif soc in existingSocials:
                request.user.social_links.filter(platform=soc).update(url=request.data[soc])
            else:
                SocialLink.objects.create(user=request.user,platform=soc,url=request.data[soc])

        return Response(
            {"updated": SocialLinkSerializer(request.user.social_links.all(), many=True).data},
            status=status.HTTP_200_OK
        )
