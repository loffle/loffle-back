from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter, APIRootView
from rest_framework.views import APIView
from rest_framework_extensions.routers import ExtendedDefaultRouter

from community.views import PostViewSet, PostCommentViewSet, ReviewViewSet, NoticeViewSet, QuestionViewSet, \
    AnswerViewSet, ReviewCommentViewSet, QuestionTypeViewSet


class CommunityAPI(APIRootView):
    """
    로플의 커뮤니티 API
    """
    pass


router = ExtendedDefaultRouter(trailing_slash=False)
router.APIRootView = CommunityAPI

router.register('posts', PostViewSet, basename='post') \
    .register('comments',
              PostCommentViewSet,
              basename='post-comment',
              parents_query_lookups=('post',))
router.register('reviews', ReviewViewSet, basename='review') \
    .register('comments',
              ReviewCommentViewSet,
              basename='review-comment',
              parents_query_lookups=('review',))
router.register('notices', NoticeViewSet, basename='notice')
router.register('questions', QuestionViewSet, basename='question') \
    .register('answers',
              AnswerViewSet,
              basename='answer',
              parents_query_lookups=('question',))
router.register('question-types', QuestionTypeViewSet, basename='question-type')

urlpatterns = [
    path('', include(router.urls)),
]
