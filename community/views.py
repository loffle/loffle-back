from django.http import QueryDict
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404, DestroyAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer
from community.permissions import IsOwnerOrReadOnly
from community.serializers import PostListSerializer, PostDetailSerializer, PostCommentListSerializer, \
    PostCommentDetailSerializer, ReviewCommentDetailSerializer, ReviewCommentListSerializer, ReviewListSerializer, \
    ReviewDetailSerializer, NoticeListSerializer, NoticeDetailSerializer, QuestionListSerializer, \
    QuestionDetailSerializer, AnswerDetailSerializer, AnswerListSerializer


class CommonViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        try:
            if self.detail is False:
                return self.serializer_list_class
            else:
                return self.serializer_detail_class
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class ChildViewSet(NestedViewSetMixin, CommonViewSet):

    def perform_create(self, serializer):
        parent_model_name = self.parent_model._meta.model_name

        pm = get_object_or_404(self.parent_model.objects.all(), pk=self.get_parents_query_dict()[parent_model_name])
        values = {
            'user': self.request.user,
            parent_model_name: pm,
        }
        serializer.save(**values)


# ===============================================================

class PostViewSet(CommonViewSet):
    queryset = Post.objects.all()

    serializer_list_class = PostListSerializer
    serializer_detail_class = PostDetailSerializer

    model = Post


class PostCommentViewSet(ChildViewSet):
    queryset = PostComment.objects.all()

    serializer_list_class = PostCommentListSerializer
    serializer_detail_class = PostCommentDetailSerializer

    parent_model = Post
    model = PostComment


class ReviewViewSet(CommonViewSet):
    queryset = Review.objects.all()

    serializer_list_class = ReviewListSerializer
    serializer_detail_class = ReviewDetailSerializer

    model = Review


class ReviewCommentViewSet(ChildViewSet):
    queryset = ReviewComment.objects.all()

    serializer_list_class = ReviewCommentListSerializer
    serializer_detail_class = ReviewCommentDetailSerializer

    parent_model = Review
    model = ReviewComment


# ---------------------------------------------------------------

class NoticeViewSet(CommonViewSet):
    queryset = Notice.objects.all()

    serializer_list_class = NoticeListSerializer
    serializer_detail_class = NoticeDetailSerializer

    model = Notice


# ---------------------------------------------------------------

class QuestionViewSet(CommonViewSet):
    queryset = Question.objects.all()

    serializer_list_class = QuestionListSerializer
    serializer_detail_class = QuestionDetailSerializer

    model = Question


class AnswerViewSet(CommonViewSet):
    queryset = Answer.objects.all()

    serializer_list_class = AnswerListSerializer
    serializer_detail_class = AnswerDetailSerializer

    model = Answer
