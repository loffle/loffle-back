from django.contrib.auth import user_logged_in
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView

from account.models import User
from account.serializers import UserSerializer


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, create = Token.objects.get_or_create(user=user)

        user_logged_in.send(sender=user.__class__, request=request, user=user)

        return Response({
            'token': token.key,
            'nickname': user.username,
        })


class LogoutView(APIView):
    def get(self, request, format=None):
        if request.auth is not None:
            request.auth.delete()
            return Response({'detail': '로그아웃 되었습니다.'}, status=HTTP_200_OK)
        else:
            return Response({'detail': '로그인 상태가 아닙니다.'}, status=HTTP_401_UNAUTHORIZED)


class SignUpView(CreateAPIView):
    model = User
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
