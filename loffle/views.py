from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST, \
    HTTP_200_OK
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from account.models import User
from loffle.models import Ticket, TicketBuy, Product, Raffle, RaffleApply
from loffle.paginations import ApplyUserPagination, RafflePagination
from loffle.permissions import IsSuperuserOrReadOnly, IsStaffOrReadOnly
from loffle.serializers import TicketSerializer, ProductSerializer, RaffleSerializer, ApplyUserSerializer


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

    @action(methods=('get',), detail=False, permission_classes=(IsAuthenticated,),
            url_path='my-ticket', url_name='my-ticket')
    def get_ticket(self, request, **kwargs):
        # obj = self.get_object()
        user = request.user

        # 티켓의 수량 가져오기
        result = {
            'num_of_tickets':
                user.buy_tickets.select_related('ticket').aggregate(buy_tickets=Coalesce(Sum('ticket__quantity'), 0))[
                    'buy_tickets'] - RaffleApply.objects.filter(user_id=user.pk).count()}
        return Response(result, status=HTTP_200_OK)


class CommonViewSet(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=HTTP_204_NO_CONTENT)


class ProductViewSet(CommonViewSet):
    permission_classes = [IsStaffOrReadOnly]  # Only Staff # TODO: obj 권한은 owner만 줄 것!

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class RaffleViewSet(CommonViewSet):
    permission_classes = [IsStaffOrReadOnly]  # Only Staff
    pagination_class = RafflePagination

    queryset = Raffle.objects.all().order_by('end_date_time')
    serializer_class = RaffleSerializer

    @action(methods=('post',), detail=True, permission_classes=(IsAuthenticated,),
            url_path='apply', url_name='apply-raffle')
    def apply_raffle(self, request, **kwargs):
        obj = self.get_object()
        # 응모 여부 검사
        if obj.applied.filter(user__pk=request.user.pk).exists():
            return Response({'detail': '이미 응모한 래플입니다.'}, status=HTTP_409_CONFLICT)
        # 티켓 소유 검사
        elif request.user.buy_tickets.select_related('ticket').aggregate(
                buy_tickets=Coalesce(Sum('ticket__quantity'), 0))[
            'buy_tickets'] - RaffleApply.objects.filter(user_id=request.user.pk).count() <= 0:
            return Response({'detail': '소유한 티켓이 없습니다.'}, status=HTTP_400_BAD_REQUEST)
        else:
            ra = RaffleApply.objects.create(
                raffle=obj,
                user=request.user,
            )
            ordinal_number = RaffleApply.objects.filter(raffle_id=ra.raffle_id,
                                                        created_at__lt=ra.created_at).count() + 1
            return Response({'detail': '래플 응모 성공✅', 'ordinal_number': ordinal_number}, status=HTTP_201_CREATED)


class ApplyUserViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    # pagination_class = ApplyUserPagination
    serializer_class = ApplyUserSerializer

    def get_queryset(self):
        return User.objects.filter(
            applied_raffles__raffle_id=self.kwargs['parent_lookup_raffle']).order_by('applied_raffles__created_at')
