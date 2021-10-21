from collections import defaultdict
from datetime import timedelta, datetime
import pytz
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.timezone import now

from account.models import User

KST = pytz.timezone('Asia/Seoul')


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
        validators=[MinValueValidator(limit_value=3)]
    )

    # lottery = models.ForeignKey(Lottery, related_name='raffles', on_delete=models.SET_NULL, null=True, default=None)
    user = models.ForeignKey(
        User,
        verbose_name='등록한 사람',
        related_name='raffles',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name='연결된 제품',
        related_name='raffles',
        on_delete=models.CASCADE
    )

    PROGRESS_CHOICES = (
        ('waiting', '응모 대기'),
        ('ongoing', '응모 진행중'),
        ('done', '응모 종료'),
        ('failed', '응모 실패')
    )
    progress = models.CharField(
        verbose_name='진행 상황',
        max_length=10,
        choices=PROGRESS_CHOICES,
        editable=False, blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    objects = CommonManager()
    deleted_objects = CommonManager(is_deleted=True)

    __original_end_date_time = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_end_date_time = self.end_date_time

    def save(self, *args, **kwargs):
        # 발표일시
        if not self.announce_date_time or self.end_date_time != self.__original_end_date_time:
            self.announce_date_time = self.get_announce_date_time()
            self.progress = self.get_progress()

        # 진행상황
        if not self.progress:
            self.progress = self.get_progress()

        super().save(*args, **kwargs)

        __original_end_date_time = self.end_date_time

    def get_announce_date_time(self):
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

    def get_progress(self):
        """
        - 조건
            - 응모 대기 (**default**)
                - 현재 일시(now)보다 시작 일시(`start_date_time`)가 클 경우
            - 응모 진행중
                - 현재 일시(now)가 시작 일시(`start_date_time`)보다 클 경우
                - 목표 수량(`target_quantity`)을 다 채우지 못했을 경우
            - 응모 종료
                - 목표 수량(`target_quantity`)을 다 채웠을 경우
            - 응모 실패
                - 목표 수량을 채우지 못하고 종료 일시(`end_date_time`)가 지날 경우
        """

        start_dt_utc = self.start_date_time  # datetime(tzinfo=<UTC>)
        end_dt_utc = self.end_date_time  # datetime(tzinfo=<UTC>)

        start_dt_kst = start_dt_utc.astimezone(KST)
        end_dt_kst = end_dt_utc.astimezone(KST)
        now_kst = datetime.now(tz=KST)

        if now_kst < start_dt_kst:
            return self.PROGRESS_CHOICES[0][0]  # 'waiting'
        elif now_kst <= end_dt_kst:
            applied_cnt = self.applied.count()  # 응모 카운트
            if applied_cnt < self.target_quantity:
                return self.PROGRESS_CHOICES[1][0]  # 'ongoing'
            else:
                return self.PROGRESS_CHOICES[2][0]  # 'done'
        else:
            return self.PROGRESS_CHOICES[3][0]  # 'failed'

    @property
    def applied_count(self):
        return self.applied.count()


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

    def clean(self):
        error_dict = defaultdict(list)

        # 응모 여부 검사
        if RaffleApply.objects.filter(raffle__pk=self.raffle.pk, user__pk=self.user.pk).exists():
            error_dict['user'].append(f'사용자 <{self.user.username}>는 이미 응모한 래플입니다.')

        # 티켓 소유 검사
        if self.user.num_tickets <= 0:
            error_dict['user'].append(f'사용자 <{self.user.username}>는 소유한 티켓이 없습니다.')

        # 응모 가능 수량 검사
        if self.raffle.applied_count >= self.raffle.target_quantity:
            error_dict['raffle'].append(f"응모 가능한 수량<{self.raffle.target_quantity}>을 초과하였습니다.")

        # 래플 상태 검사
        if self.raffle.progress != self.raffle.PROGRESS_CHOICES[1][0]:
            error_dict['raffle'].append(f'진행 상황이 <{self.raffle.get_progress_display()}>인 래플은 응모할 수 없습니다.')

        if len(error_dict) > 0:
            raise ValidationError(error_dict)

        super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 래플이 목표 수량을 채운 경우
        if self.raffle.applied_count >= self.raffle.target_quantity:
            # 래플의 진행 상황을 종료(done)로 변경
            self.raffle.progress = self.raffle.PROGRESS_CHOICES[2][0]
            self.raffle.save(update_fields=['progress'])

            # 1차 추첨 시작




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
