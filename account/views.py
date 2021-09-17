from datetime import datetime

from django.contrib.auth import authenticate, login
from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from account.serializers import SignUpSerializer


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, create = Token.objects.get_or_create(user=user)

        # TODO: 비동기로 처리할 것
        user.last_login = datetime.now()
        user.save()
        # ------------------------------

        return Response({
            'token': token.key,
            'nickname': user.username,
        })

