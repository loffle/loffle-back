from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField
from rest_framework.serializers import ModelSerializer

from _common.serializer_fields import ChildDetailUrlField, ChildListUrlField
from _common.serializers import CommonSerializer, CustomSerializer
from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer, QuestionType
from community.serializer_fields import LikeField, CommentField, AnswerField

EXCLUDE = ('is_deleted',)
READ_ONLY_FIELDS = ('user',)


class CommunitySerializer(CommonSerializer):
    pass


# ----- Post, PostComment ----- #

class PostSerializer(CommunitySerializer, LikeField, CommentField):
    class PostLinksSerializer(CustomSerializer):
        like = HyperlinkedIdentityField(view_name='post-like')
        comments = ChildListUrlField(view_name='post-comment-list')

    _links = PostLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Post
        exclude = EXCLUDE + ('like',)


class PostCommentSerializer(CommunitySerializer, LikeField):
    url = ChildDetailUrlField(view_name='post-comment-detail')

    class PostCommentLinksSerializer(CustomSerializer):
        like = ChildDetailUrlField(view_name='post-comment-like')

    _links = PostCommentLinksSerializer(source='*', read_only=True)

    class Meta:
        model = PostComment
        exclude = EXCLUDE + ('like', 'post')


# ----- Review, ReviewComment ----- #

class ReviewSerializer(CommunitySerializer, LikeField, CommentField):
    class ReviewLinksSerializer(CustomSerializer):
        like = HyperlinkedIdentityField(view_name='review-like')
        comments = ChildListUrlField(view_name='review-comment-list')

    _links = ReviewLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Review
        exclude = EXCLUDE + ('like',)


class ReviewCommentSerializer(CommunitySerializer, LikeField):
    url = ChildDetailUrlField(view_name='review-comment-detail')

    class ReviewCommentLinksSerializer(CustomSerializer):
        like = ChildDetailUrlField(view_name='review-comment-like')

    _links = ReviewCommentLinksSerializer(source='*', read_only=True)

    class Meta:
        model = ReviewComment
        exclude = EXCLUDE + ('like', 'review')


# ----- Notice ----- #

class NoticeSerializer(CommunitySerializer):
    class Meta:
        model = Notice
        exclude = EXCLUDE


# ----- Question, Answer, QuestionType ----- #
class QuestionSerializer(CommunitySerializer, AnswerField):
    question_type = StringRelatedField()

    class QuestionLinksSerializer(CustomSerializer):
        answers = ChildListUrlField(view_name='answer-list')

    _links = QuestionLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Question
        exclude = EXCLUDE  # + ('question_type',)


class AnswerSerializer(CommunitySerializer):
    url = ChildDetailUrlField(view_name='answer-detail')

    class AnswerLinksSerializer(CustomSerializer):
        pass

    _links = AnswerLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Answer
        exclude = EXCLUDE + ('question',)


class QuestionTypeSerializer(ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'
