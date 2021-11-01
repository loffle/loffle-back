from rest_framework.fields import SerializerMethodField
from _common.serializers import CustomSerializer


class LikeField(CustomSerializer):
    like_count = SerializerMethodField()
    like_or_not = SerializerMethodField()

    @staticmethod
    def get_like_count(obj):
        return obj.like.count()

    def get_like_or_not(self, obj):
        return obj.like.filter(pk=self.context['request'].user.pk).exists()


class CommentField(CustomSerializer):
    comment_count = SerializerMethodField()

    @staticmethod
    def get_comment_count(obj):
        return obj.comments.count()


class AnswerField(CustomSerializer):
    answer_count = SerializerMethodField()

    @staticmethod
    def get_answer_count(obj):
        return obj.answers.count()
