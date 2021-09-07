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

router = ExtendedDefaultRouter()
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

urlpatterns = [
    path('', include(router.urls)),

    # path('post/<int:parent_pk>/comment/',
    #      PostCommentViewSet.as_view({
    #          'get': 'list', 'post': 'create',
    #      }, suffix='List'), name='postcomment-list'),
    # path('post/<int:parent_pk>/comment/<int:pk>/',
    #      PostCommentViewSet.as_view({
    #          'delete': 'destroy',
    #      }, suffix='Detail'), name='postcomment-detail'),

    # path('review/<int:parent_pk>/comment/',
    #      ReviewCommentViewSet.as_view({
    #          'get': 'list', 'post': 'create',
    #      }, suffix='List'), name='reviewcomment-list'),
    # path('review/<int:parent_pk>/comment/<int:pk>/',
    #      ReviewCommentViewSet.as_view({
    #          'delete': 'destroy',
    #      }, suffix='Detail'), name='reviewcomment-detail'),
    #
    # path('question/<int:parent_pk>/answer/',
    #      AnswerViewSet.as_view({
    #          'get': 'list', 'post': 'create',
    #      }, suffix='List'), name='answer-list'),
    # path('question/<int:parent_pk>/answer/<int:pk>/',
    #      AnswerViewSet.as_view({
    #          'delete': 'destroy',
    #      }, suffix='Detail'), name='answer-detail'),
]
