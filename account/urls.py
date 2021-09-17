from django.urls import path

from account.views import LoginView, SignUpView, LogoutView

urlpatterns = [
    path('/login', LoginView.as_view(), name='login'),
    path('/logout', LogoutView.as_view(), name='logout'),
    path('/signup', SignUpView.as_view(), name='signup'),
]
