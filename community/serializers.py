from rest_framework.serializers import ModelSerializer

from community.models import Post, PostComment, Review, ReviewComment, Notice, Question, Answer


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        exclude = ('is_deleted',)
        read_only_fields = ('user', 'like')


class PostCommentSerializer(ModelSerializer):
    class Meta:
        model = PostComment
        exclude = ('is_deleted',)
        read_only_fields = ('post', 'user', 'like')


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
        read_only_fields = ('user',)
