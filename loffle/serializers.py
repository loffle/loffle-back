from json import loads

from rest_framework.fields import SerializerMethodField, DateTimeField
from rest_framework.relations import HyperlinkedIdentityField, StringRelatedField, PrimaryKeyRelatedField
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, Serializer
from rest_framework_extensions.fields import ResourceUriField

from _common.serializers import CommonSerializer
from account.models import User
from community.serializers.custom.fields import CommentListUrlField
from loffle.models import Ticket, Product, Raffle, RaffleCandidate, RaffleWinner


class TicketSerializer(CommonSerializer):

    class TicketLinksSerializer(Serializer):
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

    class RaffleLinksSerializer(Serializer):
        apply = HyperlinkedIdentityField(view_name='raffle-apply')
        applicants = CommentListUrlField(view_name='applicant-list')
        candidates = CommentListUrlField(view_name='candidate-list')
        winner = CommentListUrlField(view_name='winner-list')

        def create(self, validated_data):
            pass

        def update(self, instance, validated_data):
            pass

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

    class Meta:
        model = RaffleCandidate
        fields = ('user', 'given_numbers')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'given_numbers' in ret:
            ret['given_numbers'] = loads(instance.given_numbers)
        return ret


class RaffleWinnerSerializer(CommonSerializer):
    user = SerializerMethodField()

    class Meta:
        model = RaffleWinner
        fields = ('user',)

    def get_user(self, obj):
        return str(obj.raffle_candidate.user)
