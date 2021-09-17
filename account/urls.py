from django.urls import path, include
from rest_framework_extensions.routers import ExtendedDefaultRouter

from account.views import LoginView

#                 .register('comment',
#                           PostCommentViewSet,
#                           basename='post-comment',
#                           parents_query_lookups=('post',))
# router.register('review', ReviewViewSet, basename='review') \
#                 .register('comment',
#                           ReviewCommentViewSet,
#                           basename='review-comment',
#                           parents_query_lookups=('review',))
# router.register('notice', NoticeViewSet, basename='notice')
# router.register('question', QuestionViewSet, basename='question') \
#                 .register('answer',
#                           AnswerViewSet,
#                           basename='answer',
#                           parents_query_lookups=('question',))



urlpatterns = [
    # path('/', include('account.urls')),
    path('/login', LoginView.as_view(), name='login')
]
