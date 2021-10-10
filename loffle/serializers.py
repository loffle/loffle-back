from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer

from loffle.models import Ticket, Product


class TicketSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='tickets-detail')

    class Meta:
        model = Ticket
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='products-detail')
    user = StringRelatedField()

    class Meta:
        model = Product
        exclude = ('is_deleted',)
        read_only_fields = ('user',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # if 'user' in ret:
        #     ret['user'] = instance.user.username

        # list 에 detail url 포함 / detail 에 url 제외
        if self.context['view'].detail:
            ret.pop('url')
        return ret

# TODO: user -> String 필드 사용하기
# TODO: list detail에 따라서 다시 코드 정리