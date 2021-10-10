from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer, QuestionType
from community.serializers.custom.fields import LikeField, CommentField, AnswerField, CommentListUrlField, \
    CommentDetailUrlField

EXCLUDE = ('is_deleted',)
READ_ONLY_FIELDS = ('user',)

POST_COMMENT_ROF = READ_ONLY_FIELDS + ('post', 'like',)
POST_ROF = READ_ONLY_FIELDS + ('like',)
REVIEW_COMMENT_ROF = READ_ONLY_FIELDS + ('review', 'like',)
REVIEW_ROF = READ_ONLY_FIELDS + ('like',)
ANSWER_ROF = READ_ONLY_FIELDS + ('question',)


class CommonSerializer(ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'user' in ret:
            ret['user'] = instance.user.username
        if 'question_type' in ret:
            ret['question_type'] = instance.question_type.name
        return ret


# =======================================

# ----- PostComment, Post ----- #
class PostCommentListSerializer(CommonSerializer, LikeField):
    url = CommentDetailUrlField(view_name='post-comments-detail')

    class Meta:
        model = PostComment
        exclude = EXCLUDE
        read_only_fields = POST_COMMENT_ROF


class PostCommentDetailSerializer(CommonSerializer, LikeField):
    class Meta:
        model = PostComment
        exclude = EXCLUDE
        read_only_fields = POST_COMMENT_ROF


class PostListSerializer(CommonSerializer, LikeField, CommentField):
    url = HyperlinkedIdentityField(view_name='posts-detail')

    class Meta:
        model = Post
        exclude = EXCLUDE
        read_only_fields = POST_ROF


class PostDetailSerializer(CommonSerializer, LikeField, CommentField):
    comment_url = CommentListUrlField(view_name='post-comments-list')

    # comments = PostCommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        exclude = EXCLUDE
        read_only_fields = POST_ROF


# -------------------------------------------------------------------------------

# ----- ReviewComment, Review ----- #
class ReviewCommentListSerializer(CommonSerializer, LikeField):
    url = CommentDetailUrlField(view_name='review-comments-detail')

    class Meta:
        model = ReviewComment
        exclude = EXCLUDE
        read_only_fields = REVIEW_COMMENT_ROF


class ReviewCommentDetailSerializer(CommonSerializer, LikeField):
    class Meta:
        model = ReviewComment
        exclude = EXCLUDE
        read_only_fields = REVIEW_COMMENT_ROF


class ReviewListSerializer(CommonSerializer, LikeField, CommentField):
    url = HyperlinkedIdentityField(view_name='reviews-detail')

    class Meta:
        model = Review
        exclude = EXCLUDE
        read_only_fields = REVIEW_ROF


class ReviewDetailSerializer(CommonSerializer, LikeField, CommentField):
    comment_url = CommentListUrlField(view_name='review-comments-list')

    # comments = ReviewCommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        exclude = EXCLUDE
        read_only_fields = REVIEW_ROF


# -----------------------------------------------------------------------------------

# ----- Notice ----- #
class NoticeListSerializer(CommonSerializer):
    url = HyperlinkedIdentityField(view_name='notices-detail')

    class Meta:
        model = Notice
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS


class NoticeDetailSerializer(CommonSerializer):
    class Meta:
        model = Notice
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS


# -----------------------------------------------------------------

# ----- Answer, Question ----- #
class AnswerListSerializer(CommonSerializer):
    url = CommentDetailUrlField(view_name='answers-detail')

    class Meta:
        model = Answer
        exclude = EXCLUDE
        read_only_fields = ANSWER_ROF


class AnswerDetailSerializer(CommonSerializer):
    class Meta:
        model = Answer
        exclude = EXCLUDE
        read_only_fields = ANSWER_ROF


class QuestionListSerializer(CommonSerializer, AnswerField):
    url = HyperlinkedIdentityField(view_name='questions-detail')

    class Meta:
        model = Question
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS


class QuestionDetailSerializer(CommonSerializer, AnswerField):
    answer_url = CommentListUrlField(view_name='answers-list')

    # answers = AnswerListSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        exclude = EXCLUDE
        read_only_fields = READ_ONLY_FIELDS


# -----------------------------------------------------------------

class QuestionTypeSerializer(ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'
