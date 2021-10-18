from rest_framework.fields import SerializerMethodField, DateTimeField
from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField, HyperlinkedRelatedField, \
    PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from account.models import User
from community.serializers.custom.fields import CommentListUrlField
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

class RaffleProductSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='product-detail')

    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'url',)


class RaffleSerializer(CommonSerializer):
    url = HyperlinkedIdentityField(view_name='raffle-detail')
    user = StringRelatedField()

    product = PrimaryKeyRelatedField(label='연결된 제품', queryset=Product.objects.all(), write_only=True)
    product_preview = RaffleProductSerializer(source='product', read_only=True)

    apply_count = SerializerMethodField()
    apply_or_not = SerializerMethodField()
    apply_user_list_url = CommentListUrlField(view_name='apply-user-list')

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
    row_number = SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'apply_at', 'row_number')

    def get_apply_at(self, obj):
        raffle_id = self.context['view'].kwargs['parent_lookup_raffle']
        return DateTimeField().to_representation(
            obj.applied_raffles.get(raffle_id=raffle_id, user_id=obj.id).created_at)

    _row_number = 0

    def get_row_number(self, obj):
        page_size = self.context['view'].pagination_class.page_size

        page_num = self.context['request'].query_params.get('page', None)
        if isinstance(page_num, list) and len(page_num) > 1:
            page_num = page_num[-1]

        if page_num and self._row_number % page_size == 0:
            self._row_number = int(page_size) * (int(page_num) - 1)

        self._row_number += 1
        return self._row_number
