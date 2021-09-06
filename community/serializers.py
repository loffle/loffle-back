from abc import ABC

from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField, PrimaryKeyRelatedField, StringRelatedField

from rest_framework.serializers import ModelSerializer, BaseSerializer, Serializer

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer

from community.serializer_fields import CommentListUrlField, CommentDetailUrlField

EXCLUDE = ('is_deleted',)
READ_ONLY_FIELDS = ('user',)


class CommentSerializer(ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'user' in ret:
            ret['user'] = instance.user.username
        elif 'question_type' in ret:
            ret['question_type'] = str(instance.question_type)
        return ret


class LikeFieldSerializer(Serializer):
    like_count = SerializerMethodField()
    like_or_not = SerializerMethodField()

    @staticmethod
    def get_like_count(obj):
        return obj.like.count()

    def get_like_or_not(self, obj):
        return obj.like.filter(pk=self.context['request'].user.pk).exists()


# ============================================================================

# ----- PostComment, Post ----- #
class PostCommentListSerializer(CommentSerializer):
    url = CommentDetailUrlField(view_name='post-comment-detail')

    class Meta:
        model = PostComment
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('post', 'like',)


class PostCommentDetailSerializer(CommentSerializer):
    class Meta:
        model = PostComment
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('post', 'like',)


class PostListSerializer(CommentSerializer, LikeFieldSerializer):
    url = HyperlinkedIdentityField(view_name='post-detail')

    class Meta:
        model = Post
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('like',)


class PostDetailSerializer(CommentSerializer, LikeFieldSerializer):
    comment_url = CommentListUrlField(view_name='post-comment-list')
    comments = PostCommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('like',)


# -------------------------------------------------------------------------------

# ----- ReviewComment, Review ----- #
class ReviewCommentListSerializer(CommentSerializer):
    url = CommentDetailUrlField(view_name='review-comment-detail')

    class Meta:
        model = ReviewComment
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('review', 'like',)


class ReviewCommentDetailSerializer(CommentSerializer):
    class Meta:
        model = ReviewComment
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('review', 'like',)


class ReviewListSerializer(CommentSerializer, LikeFieldSerializer):
    url = HyperlinkedIdentityField(view_name='review-detail')

    class Meta:
        model = Review
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('like',)


class ReviewDetailSerializer(CommentSerializer, LikeFieldSerializer):
    comment_url = CommentListUrlField(view_name='review-comment-list')
    comments = ReviewCommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('like',)


# -----------------------------------------------------------------------------------

# ----- Notice ----- #
class NoticeListSerializer(CommentSerializer):
    url = HyperlinkedIdentityField(view_name='notice-detail')

    class Meta:
        model = Notice
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS


class NoticeDetailSerializer(CommentSerializer):
    class Meta:
        model = Notice
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS


# -----------------------------------------------------------------

# ----- Answer, Question ----- #
class AnswerListSerializer(CommentSerializer):
    url = CommentDetailUrlField(view_name='answer-detail')

    class Meta:
        model = Answer
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('question',)


class AnswerDetailSerializer(CommentSerializer):
    class Meta:
        model = Answer
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS + ('question',)


class QuestionListSerializer(CommentSerializer):
    url = HyperlinkedIdentityField(view_name='question-detail')

    class Meta:
        model = Question
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS


class QuestionDetailSerializer(CommentSerializer):
    answer_url = CommentListUrlField(view_name='answer-list')
    answers = AnswerListSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS
