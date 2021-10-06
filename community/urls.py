from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_extensions.routers import ExtendedDefaultRouter

from community.views import PostViewSet, PostCommentViewSet, ReviewViewSet, NoticeViewSet, QuestionViewSet, \
    AnswerViewSet, ReviewCommentViewSet, QuestionTypeViewSet

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
router.register('questiontype', QuestionTypeViewSet, basename='questiontype')

router.get_api_root_view().cls.__name__ = 'Community API'
router.get_api_root_view().cls.__doc__ = '로플의 커뮤니티 API'

urlpatterns = [
    path('/', include(router.urls)),
]
