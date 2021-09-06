from abc import ABC

from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField

from rest_framework.serializers import ModelSerializer, BaseSerializer, Serializer

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer

from community.serializer_fields import CommentListUrlField, CommentDetailUrlField


class CommonModelSerializer(ModelSerializer):
    class Meta:
        exclude = ('is_deleted',)
        read_only_fields = ('user',)


class LikeFieldSerializer(Serializer):
    like_count = SerializerMethodField()
    like_or_not = SerializerMethodField()

    @staticmethod
    def get_like_count(obj):
        return obj.like.count()

    def get_like_or_not(self, obj):
        return self.context['request'].user in obj.like.all()


# -------------------------------

class PostCommentListSerializer(CommonModelSerializer):
    url = CommentDetailUrlField(view_name='post-comment-detail', read_only=True)

    class Meta:
        model = PostComment
        exclude = ('is_deleted',)
        read_only_fields = ('post', 'user', 'like')


class PostCommentDetailSerializer(CommonModelSerializer):
    class Meta:
        model = PostComment
        exclude = ('is_deleted',)
        read_only_fields = ('post', 'user', 'like')


class PostListSerializer(CommonModelSerializer, LikeFieldSerializer):
    url = HyperlinkedIdentityField(view_name='post-detail', read_only=True)

    class Meta(CommonModelSerializer.Meta):
        model = Post
        # exclude = ('is_deleted',)
        # read_only_fields = ('user', 'like')
        read_only_fields = CommonModelSerializer.Meta.read_only_fields + ('like',)


class PostDetailSerializer(CommonModelSerializer, LikeFieldSerializer):
    comment_url = CommentListUrlField(view_name='post-comment-list', read_only=True)
    comments = PostCommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        exclude = ('is_deleted',)
        read_only_fields = ('user', 'like')


class ReviewSerializer(CommonModelSerializer):
    class Meta:
        model = Review
        exclude = ('is_deleted',)
        read_only_fields = ('user', 'like')


class ReviewCommentSerializer(CommonModelSerializer):
    class Meta:
        model = ReviewComment
        exclude = ('is_deleted',)
        read_only_fields = ('review', 'user', 'like')


class NoticeSerializer(CommonModelSerializer):
    class Meta:
        model = Notice
        exclude = ('is_deleted',)
        read_only_fields = ('user',)


class QuestionSerializer(CommonModelSerializer):
    class Meta:
        model = Question
        exclude = ('is_deleted',)
        read_only_fields = ('user',)


class AnswerSerializer(CommonModelSerializer):
    class Meta:
        model = Answer
        exclude = ('is_deleted',)
        read_only_fields = ('question', 'user',)
