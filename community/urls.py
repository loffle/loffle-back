from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_extensions.routers import ExtendedDefaultRouter

from community.views import PostViewSet, PostCommentViewSet, ReviewViewSet, NoticeViewSet, QuestionViewSet, \
    AnswerViewSet, ReviewCommentViewSet

# router = DefaultRouter()
# router.register('post', PostViewSet, basename='post')
# router.register('review', ReviewViewSet, basename='review')
# router.register('notice', NoticeViewSet, basename='notice')
# router.register('question', QuestionViewSet, basename='question')

router = ExtendedDefaultRouter(trailing_slash=False)
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

router.include_root_view = False

urlpatterns = [
    path('', include(router.urls)),
]
