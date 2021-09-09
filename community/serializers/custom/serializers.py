from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import Serializer, ModelSerializer


class CommonSerializer(ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'user' in ret:
            ret['user'] = instance.user.username
        elif 'question_type' in ret:
            ret['question_type'] = str(instance.question_type)
        return ret


class LikeField(Serializer):
    like_count = SerializerMethodField()
    like_or_not = SerializerMethodField()

    @staticmethod
    def get_like_count(obj):
        return obj.like.count()

    def get_like_or_not(self, obj):
        return obj.like.filter(pk=self.context['request'].user.pk).exists()


class CommentField(Serializer):
    comment_count = SerializerMethodField()

    @staticmethod
    def get_comment_count(obj):
        return obj.comments.count()


class AnswerField(Serializer):
    answer_count = SerializerMethodField()

    @staticmethod
    def get_answer_count(obj):
        return obj.answers.count()
