from django.urls import path, include
from rest_framework.routers import DefaultRouter

from community.views import PostViewSet, PostCommentViewSet, ReviewCommentViewSet, ReviewViewSet, NoticeViewSet, \
    QuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register('post', PostViewSet, basename='post')
router.register('postcomment', PostCommentViewSet)
router.register('review', ReviewViewSet)
router.register('reviewcomment', ReviewCommentViewSet)
router.register('notice', NoticeViewSet)
router.register('question', QuestionViewSet)
router.register('answer', AnswerViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
