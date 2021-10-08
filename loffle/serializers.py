from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer

from loffle.models import Ticket


class TicketSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='tickets-detail')

    class Meta:
        model = Ticket
        fields = '__all__'
