from rest_framework.relations import StringRelatedField, PrimaryKeyRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer, Serializer


class CustomSerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CommonSerializer(HyperlinkedModelSerializer):
    id = PrimaryKeyRelatedField(read_only=True)
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
