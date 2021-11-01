from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from _common.views import CommonViewSet
from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer, QuestionType
from community.paginations import CommunityPagination
from _common.permissions import IsOwnerOrReadOnly
from community.serializers import PostSerializer, PostCommentSerializer, ReviewSerializer, ReviewCommentSerializer, \
    NoticeSerializer, QuestionSerializer, AnswerSerializer, QuestionTypeSerializer


class CommunityViewSet(CommonViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]
    pagination_class = CommunityPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    filterset_fields = ('user',)
    search_fields = ('content',)
    ordering_fields = '__all__'  # ('created_at', 'like_count')
    ordering = '-created_at'

    def add_like(self, request, **kwargs):
        obj = self.get_object()
        if obj.like.filter(pk=request.user.pk).exists():
            if request.method == "DELETE":
                result = '좋아요 취소😥'
                obj.like.remove(request.user)
                return Response(status=HTTP_204_NO_CONTENT)
        elif request.method == "POST":
            result = '좋아요 성공✅'
            obj.like.add(request.user)
            return Response({'detail': result}, status=HTTP_201_CREATED)
        return Response({'detail': '잘못된 요청입니다.'}, status=HTTP_400_BAD_REQUEST)


class ChildViewSet(NestedViewSetMixin, CommunityViewSet):
    ordering = 'created_at'

    def perform_create(self, serializer):
        parent_model_name = self.parent_model._meta.model_name

        pm = get_object_or_404(self.parent_model.objects.all(), pk=self.get_parents_query_dict()[parent_model_name])
        values = {
            'user': self.request.user,
            parent_model_name: pm,
        }
        serializer.save(**values)


# ===============================================================

class PostViewSet(CommunityViewSet):
    # model = Post
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    search_fields = CommunityViewSet.search_fields + ('title',)

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='like', url_name='like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


class PostCommentViewSet(ChildViewSet):
    model = PostComment
    parent_model = Post
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='like', url_name='like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


class ReviewViewSet(CommunityViewSet):
    # model = Review
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    search_fields = CommunityViewSet.search_fields

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='like', url_name='like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


class ReviewCommentViewSet(ChildViewSet):
    model = ReviewComment
    parent_model = Review
    queryset = ReviewComment.objects.all()
    serializer_class = ReviewCommentSerializer

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='like', url_name='like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


# ---------------------------------------------------------------

class NoticeViewSet(CommunityViewSet):
    # model = Notice
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer


# ---------------------------------------------------------------

class QuestionViewSet(CommunityViewSet):
    # model = Question
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    search_fields = CommunityViewSet.search_fields + ('title',)


class AnswerViewSet(ChildViewSet):
    model = Answer
    parent_model = Question
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    search_fields = CommunityViewSet.search_fields + ('title',)


# ---------------------------------------------------------------

class QuestionTypeViewSet(ReadOnlyModelViewSet):
    """
    Question의 질문 종류

    - ReadOnly / Admin 페이지에서 관리(Create, Update, Delete)
    - 페이징 없음
    - id 순으로 정렬
    """
    queryset = QuestionType.objects.all().order_by('id')
    serializer_class = QuestionTypeSerializer
