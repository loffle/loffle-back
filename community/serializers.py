from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer

from community.serializer_fields import CommentListUrlField, CommentDetailUrlField


# -------------------------------

class PostCommentListSerializer(ModelSerializer):
    url = CommentDetailUrlField(view_name='post-comment-detail', read_only=True)

    class Meta:
        model = PostComment
        exclude = ('is_deleted',)
        read_only_fields = ('post', 'user', 'like')


class PostCommentDetailSerializer(ModelSerializer):
    class Meta:
        model = PostComment
        exclude = ('is_deleted',)
        read_only_fields = ('post', 'user', 'like')


class PostListSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='post-detail', read_only=True)

    class Meta:
        model = Post
        exclude = ('is_deleted',)
        read_only_fields = ('user', 'like')


class PostDetailSerializer(ModelSerializer):
    comment_url = CommentListUrlField(view_name='post-comment-list', read_only=True)
    comments = PostCommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        exclude = ('is_deleted',)
        read_only_fields = ('user', 'like')


class ReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        exclude = ('is_deleted',)
        read_only_fields = ('user', 'like')


class ReviewCommentSerializer(ModelSerializer):
    class Meta:
        model = ReviewComment
        exclude = ('is_deleted',)
        read_only_fields = ('review', 'user', 'like')


class NoticeSerializer(ModelSerializer):
    class Meta:
        model = Notice
        exclude = ('is_deleted',)
        read_only_fields = ('user',)


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        exclude = ('is_deleted',)
        read_only_fields = ('user',)


class AnswerSerializer(ModelSerializer):
    class Meta:
        model = Answer
        exclude = ('is_deleted',)
        read_only_fields = ('question', 'user',)
