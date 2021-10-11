from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField, HyperlinkedRelatedField
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer

from loffle.models import Ticket, Product, Raffle


class TicketSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='ticket-detail')

    class Meta:
        model = Ticket
        fields = '__all__'


# ================================================================

class CommonSerializer(ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # if 'user' in ret:
        #     ret['user'] = instance.user.username

        # list 에 detail url 포함 / detail 에 url 제외
        if self.context['view'].detail:
            ret.pop('url')
        return ret


class ProductSerializer(CommonSerializer):
    url = HyperlinkedIdentityField(view_name='product-detail')
    user = StringRelatedField()

    class Meta:
        model = Product
        exclude = ('is_deleted',)
        read_only_fields = ('user',)


# TODO: user -> String 필드 사용하기
# TODO: list detail에 따라서 다시 코드 정리

class RaffleSerializer(CommonSerializer):
    url = HyperlinkedIdentityField(view_name='raffle-detail')
    user = StringRelatedField()
    # product = ProductSerializer(read_only=True)

    # 래플 진행 상태
    # 응모 여부 apply_or_not
    # 응모한 사람 카운트 apply_count

    class Meta:
        model = Raffle
        exclude = ('is_deleted',)
        read_only_fields = ('user',)
