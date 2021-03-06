from django.contrib.auth import user_logged_in
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from account.models import User
from account.serializers import UserSerializer, MySerializer


# class UserViewSet(RetrieveModelMixin, GenericViewSet):
#     permission_classes = [IsOwner]
#
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class MyView(RetrieveUpdateAPIView):
    model = User
    queryset = User.objects.all()
    serializer_class = MySerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


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
            'id': user.id,
        })


class LogoutView(APIView):
    def get(self, request, format=None):
        if request.auth is not None:
            request.auth.delete()
            return Response({'detail': '???????????? ???????????????.'}, status=HTTP_200_OK)
        else:
            return Response({'detail': '????????? ????????? ????????????.'}, status=HTTP_401_UNAUTHORIZED)


class SignUpView(CreateAPIView):
    model = User
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # ?????? ??????(is_active=False)
        result = super().post(request, *args, **kwargs)
        return result

        # ????????? ??????
        user = User.objects.get(email=request.data['email'])
        url_kwargs = {
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': PasswordResetTokenGenerator().make_token(user),
        }

        activate_url = reverse('activate', kwargs=url_kwargs, request=request)

        subject = _(f'{user.username}???, ????????? ?????????????????????.')
        message = _(f'????????? ???????????? ????????? ?????????????????????.\n\n{activate_url}')

        email = EmailMessage(subject, message, to=[user.email])
        email.send()

        return result


class ActivateView(APIView):

    def get(self, request, uidb64, token):
        # uid ????????? ??????
        try:
            user_pk = force_text(urlsafe_base64_decode(uidb64))
        except DjangoUnicodeDecodeError:
            return Response({'detail': 'uid ?????? ???????????? ????????????.'}, status=HTTP_400_BAD_REQUEST)

        # ????????? pk ??????
        try:
            user = User.objects.get(pk=user_pk)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': '???????????? ?????? ??????????????????.'}, status=HTTP_404_NOT_FOUND)

        # ?????? ??????
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'detail': '???????????? ???????????? ????????????.'}, status=HTTP_400_BAD_REQUEST)

        # ?????? ????????? ??????
        user.is_active = True
        user.save()
        return Response(status=HTTP_200_OK)


class CheckUserInfoView(APIView):
    """
    ????????? ?????? ?????? ??????
    - email
    - username
    - phone
    """

    def post(self, request, info):
        result = {}
        check_list = ['email', 'username', 'phone']
        if info not in check_list:
            return Response({'detail': '???????????? ?????? ???????????????.'}, status=HTTP_404_NOT_FOUND)

        value = request.POST.get(info, '')
        if value:
            result[info + '_exist'] = User.objects.filter(**{info: value}).exists()

        if not result:
            return Response({'detail': f'{info} ?????? ???????????????.'}, status=HTTP_400_BAD_REQUEST)

        return Response(result, status=HTTP_200_OK)
