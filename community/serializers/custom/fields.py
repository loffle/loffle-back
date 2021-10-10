from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedRelatedField, HyperlinkedIdentityField
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer
from rest_framework_extensions.settings import extensions_api_settings


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


class CommentListUrlField(HyperlinkedIdentityField):
    parent_kwarg_prefix = extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            self.parent_kwarg_prefix + obj._meta.model_name: obj.pk,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    # def get_object(self, view_name, view_args, view_kwargs):
    #     lookup_kwargs = {
    #         f'post__pk': view_kwargs[self.parent_kwarg_name],
    #     }
    #     return self.get_queryset().get(**lookup_kwargs)


class CommentDetailUrlField(HyperlinkedIdentityField):
    parent_kwarg_prefix = extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX

    def get_url(self, obj, view_name, request, format):
        try:
            self.context['view'].parent_model
            # if view's model == child model
            parent_kwarg_name = self.parent_kwarg_prefix + self.context['view'].parent_model._meta.model_name
            parent_kwarg_value = self.context['view'].kwargs[parent_kwarg_name]
        except AttributeError:
            # if view's model == parent model
            parent_kwarg_name = self.parent_kwarg_prefix + self.context['view'].model._meta.model_name
            parent_kwarg_value = self.context['view'].kwargs['pk']

        url_kwargs = {
            parent_kwarg_name: parent_kwarg_value,  # obj.post.pk,
            'pk': obj.pk
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    # def get_object(self, view_name, view_args, view_kwargs):
    #     lookup_kwargs = {
    #         'post__pk': view_kwargs['parent_lookup_post'],
    #         'pk': view_kwargs['pk']
    #     }
    #     return self.get_queryset().get(**lookup_kwargs)
