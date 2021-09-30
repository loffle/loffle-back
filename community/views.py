from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer, QuestionType
from community.paginations import CommunityPagination
from community.permissions import IsOwnerOrReadOnly
from community.serializers.serializers import PostListSerializer, PostDetailSerializer, PostCommentListSerializer, \
    PostCommentDetailSerializer, ReviewCommentDetailSerializer, ReviewCommentListSerializer, ReviewListSerializer, \
    ReviewDetailSerializer, NoticeListSerializer, NoticeDetailSerializer, QuestionListSerializer, \
    QuestionDetailSerializer, AnswerDetailSerializer, AnswerListSerializer, QuestionTypeSerializer


class CommonViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly & IsOwnerOrReadOnly]
    pagination_class = CommunityPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    filterset_fields = ('user',)
    search_fields = ('content',)
    ordering_fields = '__all__'  # ('created_at', 'like_count')
    ordering = '-created_at'

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


class ChildViewSet(NestedViewSetMixin, CommonViewSet):
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

class PostViewSet(CommonViewSet):
    queryset = Post.objects.all()

    serializer_list_class = PostListSerializer
    serializer_detail_class = PostDetailSerializer

    model = Post

    search_fields = CommonViewSet.search_fields + ('title',)

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='add-like', url_name='add-like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


class PostCommentViewSet(ChildViewSet):
    queryset = PostComment.objects.all()

    serializer_list_class = PostCommentListSerializer
    serializer_detail_class = PostCommentDetailSerializer

    parent_model = Post
    model = PostComment

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='add-like', url_name='add-like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


class ReviewViewSet(CommonViewSet):
    queryset = Review.objects.all()

    serializer_list_class = ReviewListSerializer
    serializer_detail_class = ReviewDetailSerializer

    model = Review

    search_fields = CommonViewSet.search_fields

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='add-like', url_name='add-like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


class ReviewCommentViewSet(ChildViewSet):
    queryset = ReviewComment.objects.all()

    serializer_list_class = ReviewCommentListSerializer
    serializer_detail_class = ReviewCommentDetailSerializer

    parent_model = Review
    model = ReviewComment

    @action(methods=('post', 'delete'), detail=True, permission_classes=(IsAuthenticated,),
            url_path='add-like', url_name='add-like')
    def add_like(self, request, **kwargs):
        return super().add_like(request, **kwargs)


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

    search_fields = CommonViewSet.search_fields + ('title',)


class AnswerViewSet(ChildViewSet):
    queryset = Answer.objects.all()

    serializer_list_class = AnswerListSerializer
    serializer_detail_class = AnswerDetailSerializer

    parent_model = Question
    model = Answer

    search_fields = CommonViewSet.search_fields + ('title',)


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
