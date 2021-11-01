from django.urls import path, include
from rest_framework.routers import APIRootView
from rest_framework_extensions.routers import ExtendedDefaultRouter

from account.views import LoginView, SignUpView, LogoutView, ActivateView, CheckUserInfoView, MyView


class AccountAPI(APIRootView):
    """
    로플의 계정 API
    """
    pass


router = ExtendedDefaultRouter(trailing_slash=False)
router.APIRootView = AccountAPI

# router.register('users', UserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),

    path('my', MyView.as_view(), name='my'),

    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('signup', SignUpView.as_view(), name='signup'),

    path('activate/<str:uidb64>/<str:token>', ActivateView.as_view(), name='activate'),
    path('check-<str:info>', CheckUserInfoView.as_view(), name='check-user-info'),
]
