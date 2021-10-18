from datetime import timedelta
import pytz
from django.db import models
from django.utils import timezone
from django.utils.timezone import now

from account.models import User


class CommonManager(models.Manager):

    def __init__(self, is_deleted=False):
        super().__init__()
        self.is_deleted = is_deleted

    def get_queryset(self):
        return super().get_queryset().select_related('user').filter(is_deleted=self.is_deleted)


class Ticket(models.Model):
    quantity = models.PositiveIntegerField(
        verbose_name='수량'
    )
    price = models.PositiveBigIntegerField(
        verbose_name='가격'
    )


class TicketBuy(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        related_name='buy_tickets',
        on_delete=models.RESTRICT,
    )
    user = models.ForeignKey(
        User,
        related_name='buy_tickets',
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    objects = CommonManager()
    deleted_objects = CommonManager(is_deleted=True)

    class Meta:
        db_table = '_'.join((__package__, 'ticket_buy'))


class Product(models.Model):
    name = models.CharField(
        verbose_name='이름',
        max_length=200,
    )
    size = models.CharField(
        verbose_name='사이즈',
        max_length=100,
    )
    brand = models.CharField(
        verbose_name='브랜드',
        max_length=100,
    )
    serial = models.CharField(
        verbose_name='시리얼 번호',
        max_length=100,
    )
    color = models.CharField(
        verbose_name='색상',
        max_length=100,
    )
    release_date = models.DateField(
        verbose_name='릴리즈 날짜',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey(User, related_name="products", on_delete=models.CASCADE)
    # file = models.ManyToManyField(File, on_delete=models.SET_NULL, null=True, blank=True)  # File

    objects = CommonManager()
    deleted_objects = CommonManager(is_deleted=True)

    def __str__(self):
        return f"{self.name} | {self.brand} | {self.color} | {self.size}"


# class RaffleProgress(models.Model):
#     name = models.CharField(
#         verbose_name='진행 상황',
#         max_length=10,
#         choices=(
#             ('waiting', '응모 대기'),
#             ('ongoing', '응모 진행중'),
#             ('done', '응모 종료'),
#             ('failed', '응모 실패'),
#         ),
#         default='waiting',
#     )
#
#     class Meta:
#         db_table = '_'.join((__package__, 'raffle_progress'))


class Raffle(models.Model):
    start_date_time = models.DateTimeField(
        verbose_name='응모 시작 날짜',
    )
    end_date_time = models.DateTimeField(
        verbose_name='응모 종료 날짜',
    )
    announce_date_time = models.DateTimeField(
        verbose_name='당첨 발표 날짜',
        editable=False, blank=True,
    )
    target_quantity = models.PositiveIntegerField(
        verbose_name='목표 티켓 수량',
    )

    # lottery = models.ForeignKey(Lottery, related_name='raffles', on_delete=models.SET_NULL, null=True, default=None)
    user = models.ForeignKey(User,
                             verbose_name='등록한 사람',
                             related_name='raffles',
                             on_delete=models.CASCADE
                             )
    product = models.ForeignKey(Product,
                                verbose_name='연결된 제품',
                                related_name='raffles',
                                on_delete=models.CASCADE
                                )

    # progress = models.ForeignKey(RaffleProgress,
    #                              verbose_name='진행 상황',
    #                              related_name='raffles',
    #                              on_delete=models.PROTECT,
    #                              default=1
    #                              )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    objects = CommonManager()
    deleted_objects = CommonManager(is_deleted=True)

    def save(self, *args, **kwargs):
        self.announce_date_time = self.get_announce_date_time()
        return super().save(*args, **kwargs)

    def get_announce_date_time(self):
        KST = pytz.timezone('Asia/Seoul')
        end_dt_utc = self.end_date_time  # datetime(tzinfo=<UTC>)
        end_dt_kst = end_dt_utc.astimezone(KST)

        # weekday() -> 0: Mon, 1: Tue, ..., 4: Fri, 5: Sat, 6: Sun
        this_sat_dt = end_dt_kst + timedelta(days=5 - end_dt_kst.weekday())
        this_sat_midnight_dt = this_sat_dt.replace(hour=0, minute=1)

        # 이번주 토요일 자정까지는 이번주 토요일 21:00
        #                이후는 다음주 토요일 09:00
        this_sat_announce_dt = this_sat_dt.replace(hour=21, minute=0, second=0)
        next_sat_announce_dt = this_sat_announce_dt + timedelta(days=7)

        if end_dt_kst < this_sat_midnight_dt:
            return this_sat_announce_dt
        else:
            return next_sat_announce_dt


class RaffleApply(models.Model):
    raffle = models.ForeignKey(
        Raffle,
        verbose_name='응모한 래플',
        related_name='applied',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='응모한 사람',
        related_name='applied_raffles',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    objects = CommonManager()
    deleted_objects = CommonManager(is_deleted=True)

    class Meta:
        db_table = '_'.join((__package__, 'raffle_apply'))

    def __str__(self):
        return f'RaffleApply ({self.pk}) | {self.raffle} | {self.user}'


class RaffleCandidate(models.Model):
    raffle = models.ForeignKey(Raffle,
                               verbose_name='래플',
                               related_name='candidates',
                               on_delete=models.CASCADE,
                               )
    user = models.ForeignKey(User,
                             verbose_name='1차 당첨자',
                             related_name='candidate_raffles',
                             on_delete=models.CASCADE,
                             )

    class Meta:
        db_table = '_'.join((__package__, 'raffle_candidate'))


class RaffleWinner(models.Model):
    raffle_candidate = models.OneToOneField(RaffleCandidate,
                                            verbose_name='최종 당첨자',
                                            on_delete=models.CASCADE,
                                            )

    class Meta:
        db_table = '_'.join((__package__, 'raffle_winner'))
