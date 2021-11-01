from json import loads

from rest_framework.fields import SerializerMethodField, DateTimeField
from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField, PrimaryKeyRelatedField
from rest_framework.serializers import HyperlinkedModelSerializer

from _common.serializers import CommonSerializer, CustomSerializer
from account.models import User
from _common.serializer_fields import ChildListUrlField
from loffle.models import Ticket, Product, Raffle, RaffleCandidate, RaffleWinner


class TicketSerializer(CommonSerializer):

    class TicketLinksSerializer(CustomSerializer):
        buy = HyperlinkedIdentityField(view_name='ticket-buy')

    _links = TicketLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'


class ProductSerializer(CommonSerializer):

    class Meta:
        model = Product
        exclude = ('is_deleted',)


class RaffleProductSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = ('url', 'id', 'name', 'brand',)


class RaffleSerializer(CommonSerializer):

    product = PrimaryKeyRelatedField(label='연결된 제품', queryset=Product.objects.all(), write_only=True)
    product_preview = RaffleProductSerializer(source='product', read_only=True)

    apply_count = SerializerMethodField()
    apply_or_not = SerializerMethodField()

    class RaffleLinksSerializer(CustomSerializer):
        apply = HyperlinkedIdentityField(view_name='raffle-apply')
        applicants = ChildListUrlField(view_name='applicant-list')
        candidates = ChildListUrlField(view_name='candidate-list')
        winner = ChildListUrlField(view_name='winner-list')

    _links = RaffleLinksSerializer(source='*', read_only=True)

    class Meta:
        model = Raffle
        exclude = ('is_deleted',)

    @staticmethod
    def get_apply_count(obj):
        return obj.applied.count()

    def get_apply_or_not(self, obj):
        return obj.applied.filter(user__pk=self.context['request'].user.pk).exists()


class RaffleApplicantSerializer(CommonSerializer):
    user = StringRelatedField(source='username')
    apply_at = SerializerMethodField()

    class Meta:
        model = User
        fields = ('user', 'apply_at')

    def get_apply_at(self, obj):
        raffle_id = self.context['view'].kwargs['parent_lookup_raffle']
        return DateTimeField().to_representation(
            obj.applied_raffles.get(raffle_id=raffle_id, user_id=obj.id).created_at)


class RaffleCandidateSerializer(CommonSerializer):
    user = StringRelatedField(source='raffle_apply.user', read_only=True)

    class Meta:
        model = RaffleCandidate
        fields = ('user', 'given_numbers')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'given_numbers' in ret:
            ret['given_numbers'] = loads(instance.given_numbers)
        return ret


class RaffleWinnerSerializer(CommonSerializer):
    user = StringRelatedField(source='raffle_candidate.raffle_apply.user')

    class Meta:
        model = RaffleWinner
        fields = ('user',)
