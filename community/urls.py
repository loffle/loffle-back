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

router.register('posts', PostViewSet, basename='posts') \
    .register('comments',
              PostCommentViewSet,
              basename='post-comments',
              parents_query_lookups=('posts',))
router.register('reviews', ReviewViewSet, basename='reviews') \
    .register('comments',
              ReviewCommentViewSet,
              basename='review-comments',
              parents_query_lookups=('review',))
router.register('notices', NoticeViewSet, basename='notices')
router.register('questions', QuestionViewSet, basename='questions') \
    .register('answers',
              AnswerViewSet,
              basename='answers',
              parents_query_lookups=('question',))
router.register('question-types', QuestionTypeViewSet, basename='question-types')

urlpatterns = [
    path('/', include(router.urls)),
]
