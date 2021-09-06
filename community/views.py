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


# --------------------------------------------------

class PostViewSet(CommonViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostCommentViewSet(CommonViewSet):
    # queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer

    def get_queryset(self):
        return PostComment.objects.filter(post=self.kwargs['parent_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        post=Post.objects.get(pk=self.kwargs['parent_pk'])
                        )


class ReviewViewSet(CommonViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewCommentViewSet(CommonViewSet):
    # queryset = ReviewComment.objects.all()
    serializer_class = ReviewCommentSerializer

    def get_queryset(self):
        return ReviewComment.objects.filter(review=self.kwargs['parent_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        review=Review.objects.get(pk=self.kwargs['parent_pk'])
                        )


class NoticeViewSet(CommonViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer


class QuestionViewSet(CommonViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(CommonViewSet):
    # queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(question=self.kwargs['parent_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        question=Question.objects.get(pk=self.kwargs['parent_pk'])
                        )
