from django.core.exceptions import ValidationError
from django.db.models import Case, When, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST, \
    HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from account.models import User
from loffle.models import Ticket, TicketBuy, Product, Raffle, RaffleApply, RaffleCandidate, RaffleWinner
from loffle.paginations import ApplyUserPagination, RafflePagination
from loffle.permissions import IsSuperuserOrReadOnly, IsStaffOrReadOnly
from loffle.serializers import TicketSerializer, ProductSerializer, RaffleSerializer, ApplicantSerializer, \
    RaffleCandidateSerializer, RaffleWinnerSerializer


class TicketViewSet(ModelViewSet):
    permission_classes = [IsSuperuserOrReadOnly]

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(methods=('post',), detail=True, permission_classes=(IsAuthenticated,), serializer_class=Serializer,
            url_path='buy', url_name='buy-ticket')
    def buy_ticket(self, request, **kwargs):
        ticket = self.get_object()
        ticket_buy = TicketBuy.objects.create(
            ticket=ticket,
            user=request.user,
        )
        return Response({'detail': '티켓 구매 성공✅'}, status=HTTP_201_CREATED)

    @action(methods=('get',), detail=False, permission_classes=(IsAuthenticated,), serializer_class=Serializer,
            url_path='my-ticket', url_name='my-ticket')
    def get_ticket(self, request, **kwargs):
        # obj = self.get_object()
        user = request.user

        # 티켓의 수량 가져오기
        result = {
            'num_buy_tickets': user.num_buy_tickets,
            'num_use_tickets': user.num_use_tickets,
            'num_return_tickets': user.num_return_tickets,
            'num_tickets': user.num_tickets,
        }
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

    serializer_class = RaffleSerializer
    queryset = Raffle.objects.all()

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        ordering_keys_iter = iter(Raffle.PROGRESS_ORDERING.keys())
        ordering_values_iter = iter(Raffle.PROGRESS_ORDERING.values())

        # 'ongoing'
        qs1 = qs.filter(progress=next(ordering_keys_iter)).order_by('end_date_time') \
            .annotate(
            rank=Value(next(ordering_values_iter))
        )

        # 'waiting'
        qs2 = qs.filter(progress=next(ordering_keys_iter)).order_by('start_date_time') \
            .annotate(
            rank=Value(next(ordering_values_iter))
        )

        # 'done', 'failed'
        qs3 = qs.filter(progress__in=list(Raffle.PROGRESS_ORDERING.keys())[2:]) \
            .order_by('-end_date_time') \
            .annotate(
            rank=Case(
                When(progress=next(ordering_keys_iter), then=Value(next(ordering_values_iter))),
                When(progress=next(ordering_keys_iter), then=Value(next(ordering_values_iter))),
                default=Value(99),
            )
        )

        # result = qs1.union(qs2, qs3)
        query_list = [*qs1, *qs2, *qs3]

        page = self.paginate_queryset(query_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(query_list, many=True)
        return Response(serializer.data)

    @action(methods=('post',), detail=True, permission_classes=(IsAuthenticated,), serializer_class=Serializer,
            url_path='apply', url_name='apply-raffle')
    def apply_raffle(self, request, **kwargs):
        obj = self.get_object()
        applied_cnt = obj.applied_count  # 현재 래플에 응모된 티켓 수량

        # RaffleApply 객체 생성하여 저장할 때 clean() 메소드에서 응모 가능 조건들 검사
        # 조건: 응모 여부 / 래플 상태 / 티켓 소유 / 응모 가능 수량
        ra = RaffleApply(raffle=obj, user=request.user)
        try:
            ra.full_clean()
        except ValidationError as e:
            return Response(e.message_dict, status=HTTP_400_BAD_REQUEST)
        ra.save()

        ordinal_number = applied_cnt + 1
        return Response({'detail': '래플 응모 성공✅', 'ordinal_number': ordinal_number}, status=HTTP_201_CREATED)

    @action(methods=('post',), detail=True, permission_classes=(AllowAny,), serializer_class=Serializer,
            url_path='refresh-progress', url_name='refresh-raffle-progress')
    def refresh_raffle_progress(self, request, **kwargs):
        """
        래플 상태를 새로고침 (임시)
        """
        obj = self.get_object()
        prev_progress = obj.get_progress_display()

        obj.progress = None
        obj.save()

        now_progress = obj.get_progress_display()

        if prev_progress != now_progress:
            message = f'래플 상태가 변경되었습니다. prev:{prev_progress} -> now:{now_progress}'
        else:
            message = f'래플 상태가 변경되지 않았습니다.'
        return Response({'detail': message}, status=HTTP_200_OK)


class ApplyUserViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    # pagination_class = ApplyUserPagination
    serializer_class = ApplyUserSerializer

    def get_queryset(self):
        return User.objects.filter(
            applied_raffles__raffle_id=self.kwargs['parent_lookup_raffle']).order_by('applied_raffles__created_at')


class RaffleCandidateViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = RaffleCandidateSerializer

    def get_queryset(self):
        return RaffleCandidate.objects.filter(raffle_id=self.kwargs['parent_lookup_raffle'])


class RaffleWinnerViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = RaffleWinnerSerializer

    def get_queryset(self):
        return RaffleWinner.objects.filter(
            raffle_candidate__raffle_id=self.kwargs['parent_lookup_raffle'])
