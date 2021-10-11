from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_409_CONFLICT
from rest_framework.viewsets import ModelViewSet

from loffle.models import Ticket, TicketBuy, Product, Raffle, RaffleApply
from loffle.permissions import IsSuperuserOrReadOnly, IsStaffOrReadOnly
from loffle.serializers import TicketSerializer, ProductSerializer, RaffleSerializer


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


class CommonViewSet(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=HTTP_204_NO_CONTENT)


class ProductViewSet(CommonViewSet):
    permission_classes = [IsStaffOrReadOnly]  # Only Staff

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class RaffleViewSet(CommonViewSet):
    permission_classes = [IsStaffOrReadOnly]  # Only Staff

    queryset = Raffle.objects.all()
    serializer_class = RaffleSerializer

    @action(methods=('post',), detail=True, permission_classes=(IsAuthenticated,),
            url_path='apply', url_name='apply-raffle')
    def apply_raffle(self, request, **kwargs):
        obj = self.get_object()
        # 응모 여부 검사
        if obj.applied.filter(user__pk=request.user.pk).exists():
            return Response({'detail': '이미 응모한 래플입니다.'}, status=HTTP_409_CONFLICT)
        # 티켓 소유 검사
        elif request.user.buy_tickets.select_related('ticket').aggregate(buy_tickets=Sum('ticket__quantity'))[
                                  'buy_tickets'] - RaffleApply.objects.filter(user_id=request.user.pk).count() <= 0:
            return Response({'detail': '소유한 티켓이 없습니다.'})
        else:
            RaffleApply.objects.create(
                raffle=obj,
                user=request.user,
            )
            return Response({'detail': '래플 응모 성공✅'}, status=HTTP_201_CREATED)
