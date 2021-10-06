from rest_framework.serializers import ModelSerializer

from loffle.models import Ticket


class TicketSerializer(ModelSerializer):

    class Meta:
        model = Ticket
        exclude = ('buy',)
        # read_only_fields = ('buy',)