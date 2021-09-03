from django.http import QueryDict
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404, DestroyAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer
from community.permissions import IsOwnerOrReadOnly
from community.serializers import PostSerializer, PostCommentSerializer, ReviewSerializer, ReviewCommentSerializer, \
    NoticeSerializer, QuestionSerializer, AnswerSerializer


class CommonViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=HTTP_204_NO_CONTENT)


class ChildViewSet(CommonViewSet):

    def get_queryset(self):
        filters = {
            self.parent_model._meta.model_name: self.kwargs['parent_pk']
        }
        return self.model.objects.filter(**filters)

    def perform_create(self, serializer):
        values = {
            'user': self.request.user,
            self.parent_model._meta.model_name: self.parent_model.objects.get(pk=self.kwargs['parent_pk'])
        }
        serializer.save(**values)


# --------------------------------------------------

class PostViewSet(CommonViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostCommentViewSet(ChildViewSet):
    serializer_class = PostCommentSerializer

    parent_model = Post
    model = PostComment


class ReviewViewSet(CommonViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewCommentViewSet(ChildViewSet):
    serializer_class = ReviewCommentSerializer

    parent_model = Review
    model = ReviewComment


class NoticeViewSet(CommonViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer


class QuestionViewSet(CommonViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(ChildViewSet):
    serializer_class = AnswerSerializer

    parent_model = Question
    model = Answer
