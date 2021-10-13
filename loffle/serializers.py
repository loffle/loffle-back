from rest_framework.fields import SerializerMethodField, DateTimeField
from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField, HyperlinkedRelatedField
from rest_framework.serializers import ModelSerializer

from account.models import User
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
    # product = HyperlinkedRelatedField(view_name='product-detail', read_only=True)
    # product = HyperlinkedRelatedField(view_name='product-detail', read_only=True, lookup_field='product_id')

    apply_count = SerializerMethodField()
    apply_or_not = SerializerMethodField()

    # 래플 진행 상태
    # 응모 여부 apply_or_not
    # 응모한 사람 카운트 apply_count

    class Meta:
        model = Raffle
        exclude = ('is_deleted',)
        read_only_fields = ('user',)

    @staticmethod
    def get_apply_count(obj):
        return obj.applied.count()

    def get_apply_or_not(self, obj):
        return obj.applied.filter(user__pk=self.context['request'].user.pk).exists()


class ApplyUserSerializer(ModelSerializer):
    apply_at = SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'apply_at',)

    def get_apply_at(self, obj):
        raffle_id = self.context['view'].kwargs['parent_lookup_raffle']
        return DateTimeField().to_representation(obj.applied_raffles.get(raffle_id=raffle_id, user_id=obj.id).created_at)
