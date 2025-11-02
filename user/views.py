from django.urls import reverse

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

class Register(APIView):
    def post(self, request):
        return Response({
            'register': 'dummy'
        })

class Login(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        response.set_cookie(
            key='refresh_token',
            value=response.data['refresh'],
            path=reverse('user_refresh'),
            max_age=60 * 60 * 24 * 7, # One Week
            samesite='None',
            httponly=True,
            secure=True,
        )

        response.data['token'] = response.data['access']
        del response.data['refresh']
        del response.data['access']
        return response

class Refresh(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        response.data['token'] = response.data['access']
        del response.data['access']
        return response
