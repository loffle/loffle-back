from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer


class CommonSerializer(HyperlinkedModelSerializer):
    user = StringRelatedField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # list
        if self.context['view'].detail is False:
            if '_links' in ret:
                ret.pop('_links')

        # detail
        elif self.context['view'].detail is True:
            if '_links' in ret:
                ret.move_to_end('_links')
            if 'url' in ret:
                ret.pop('url')
        return ret
