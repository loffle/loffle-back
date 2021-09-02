from django.urls import path

from community import views

urlpatterns = [
    path('post', views.PostList.as_view(), name='post_list'),
    path('post/<int:pk>', views.PostDetail.as_view()),
]