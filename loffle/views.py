from django.shortcuts import render
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from loffle.models import Ticket
from loffle.serializers import TicketSerializer


class TicketViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
