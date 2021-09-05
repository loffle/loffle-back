from rest_framework.relations import HyperlinkedRelatedField, HyperlinkedIdentityField
from rest_framework.reverse import reverse


class CommentListUrlField(HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'parent_lookup_post': obj.pk,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'post__pk': view_kwargs['parent_lookup_post'],
        }
        return self.get_queryset().get(**lookup_kwargs)


class CommentDetailUrlField(HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'parent_lookup_post': obj.post.pk,
            'pk': obj.pk
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            'post__pk': view_kwargs['parent_lookup_post'],
            'pk': view_kwargs['pk']
        }
        return self.get_queryset().get(**lookup_kwargs)
