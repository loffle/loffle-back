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

router.register('post', PostViewSet, basename='post') \
    .register('comment',
              PostCommentViewSet,
              basename='post-comment',
              parents_query_lookups=('post',))
router.register('review', ReviewViewSet, basename='review') \
    .register('comment',
              ReviewCommentViewSet,
              basename='review-comment',
              parents_query_lookups=('review',))
router.register('notice', NoticeViewSet, basename='notice')
router.register('question', QuestionViewSet, basename='question') \
    .register('answer',
              AnswerViewSet,
              basename='answer',
              parents_query_lookups=('question',))
router.register('questiontype', QuestionTypeViewSet, basename='questiontype')

urlpatterns = [
    path('/', include(router.urls)),
]
