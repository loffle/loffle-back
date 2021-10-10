from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet

from loffle.models import Ticket, TicketBuy, Product
from loffle.permissions import IsSuperuserOrReadOnly, IsStaffOrReadOnly
from loffle.serializers import TicketSerializer, ProductSerializer


class TicketViewSet(ModelViewSet):
    permission_classes = [IsSuperuserOrReadOnly]

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(methods=('post',), detail=True, permission_classes=(IsAuthenticated,),
            url_path='buy', url_name='buy-ticket')
    def buy_ticket(self, request, **kwargs):
        ticket = self.get_object()
        ticket_buy = TicketBuy.objects.create(
            ticket=ticket,
            user=request.user,
        )
        return Response({'detail': '티켓 구매 성공✅'}, status=HTTP_201_CREATED)


class ProductViewSet(ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]  # Only Staff

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=HTTP_204_NO_CONTENT)
