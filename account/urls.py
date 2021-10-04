from django.urls import path

from account.views import LoginView, SignUpView, LogoutView, ActivateView, CheckUserView

urlpatterns = [
    path('/login', LoginView.as_view(), name='login'),
    path('/logout', LogoutView.as_view(), name='logout'),
    path('/signup', SignUpView.as_view(), name='signup'),

    path('/activate/<str:uidb64>/<str:token>', ActivateView.as_view(), name='activate'),
    path('/check-user', CheckUserView.as_view(), name='check-user'),
]
