from collections import defaultdict
from datetime import timedelta, datetime
from json import dumps
from random import sample

import requests
from django.db.models import Exists
from pytz import timezone as pytz_tz
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from account.models import User

KST = pytz_tz('Asia/Seoul')


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
    PROGRESS_ORDERING = {
        # ongoing
        PROGRESS_CHOICES[1][0]: 1,
        # waiting
        PROGRESS_CHOICES[0][0]: 2,
        # done
        PROGRESS_CHOICES[2][0]: 3,
        # failed
        PROGRESS_CHOICES[3][0]: 4,
    }  # python 3.7+ dict 삽입 순서 유지

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    objects = CommonManager()
    deleted_objects = CommonManager(is_deleted=True)

    @property
    def applied_count(self):
        return self.applied.count()

    @property
    def candidates_count(self):
        return self.candidates.count()

    __original_end_date_time = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_end_date_time = self.end_date_time

    def save(self, *args, **kwargs):
        # 발표일시
        if not self.announce_date_time or self.end_date_time != self.__original_end_date_time:
            self.announce_date_time = self.calc_announce_date_time()
            self.progress = self.calc_progress()

        # 진행상황
        if not self.progress:
            self.progress = self.calc_progress()

        super().save(*args, **kwargs)

        __original_end_date_time = self.end_date_time

    def calc_announce_date_time(self, done_date_time=None):
        end_dt_utc = self.end_date_time  # datetime(tzinfo=<UTC>)
        if done_date_time:
            end_dt_utc = done_date_time
        end_dt_kst = end_dt_utc.astimezone(KST)

        # weekday() -> 0: Mon, 1: Tue, ..., 4: Fri, 5: Sat, 6: Sun
        this_sat_dt = end_dt_kst + timedelta(days=5 - end_dt_kst.weekday())
        this_sat_midnight_dt = this_sat_dt.replace(hour=0, minute=1)

        # 이번주 토요일 자정까지는 이번주 토요일 21:00
        #                이후는 다음주 토요일 21:00
        this_sat_announce_dt = this_sat_dt.replace(hour=21, minute=0, second=0)
        next_sat_announce_dt = this_sat_announce_dt + timedelta(days=7)

        if end_dt_kst < this_sat_midnight_dt:
            return this_sat_announce_dt
        else:
            return next_sat_announce_dt

    def calc_progress(self):
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
            return Raffle.PROGRESS_CHOICES[0][0]  # 'waiting'
        elif now_kst <= end_dt_kst:
            if self.applied_count < self.target_quantity:
                return Raffle.PROGRESS_CHOICES[1][0]  # 'ongoing'
            else:
                return Raffle.PROGRESS_CHOICES[2][0]  # 'done'
        else:
            return Raffle.PROGRESS_CHOICES[3][0]  # 'failed'

    CANDIDATES_N = (45, 15, 9, 5, 3)  # 45의 약수(divisor)

    def create_candidates(self):
        # 래플 상태가 done(완료) 인지 확인
        if self.progress != Raffle.PROGRESS_CHOICES[2][0]:
            return False

        # 래플의 후보자가 존재하면 이미 추첨이 진행되었다고 판단
        if self.candidates_count > 0:
            print('이미 진행된 추첨이 존재합니다.')
            return False

        # 45의 약수 중 목표 수량(target_quantity)에서 제일 가까운 수를 [n: 후보자의 수]로 설정
        for num_candidates in Raffle.CANDIDATES_N:
            if self.target_quantity >= num_candidates:
                break

        # 응모자를 후보자의 수로 추려내기
        applicants_id_list = list(self.applied.select_related('user').values_list('user_id', flat=True))
        candidates_id_list = sample(applicants_id_list, num_candidates)

        candidates_list = []
        num_given_numbers = 45 // num_candidates
        for i, user_id in enumerate(candidates_id_list):
            given_numbers = [j + i * num_given_numbers for j in range(1, num_given_numbers + 1)]
            candidates_list.append(
                RaffleCandidate(raffle_id=self.pk, user_id=user_id, given_numbers=dumps(given_numbers)))

        RaffleCandidate.objects.bulk_create(candidates_list)
        return True

    def draw_winner(self):
        """
        (임시) 래플 당첨자 추첨하기
        """
        now_utc = datetime.now()
        now_kst = now_utc.astimezone(KST)
        if now_kst <= self.announce_date_time:
            raise Exception("발표일시가 지나지 않았습니다.")

        if self.progress != self.PROGRESS_CHOICES[2][0]:
            raise Exception("종료된 상태의 래플만 가능합니다.")

        qs = Lotto.objects.filter(draw_date=self.announce_date_time)
        if not Exists(qs):
            raise Exception("로또 번호가 존재하지 않습니다.")

        bonus_num = qs.first().bonus_num
        candidate_winner = self.candidates.filter(given_numbers__contains=bonus_num)
        rw = RaffleWinner(raffle_candidate=candidate_winner)
        rw.save()


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
        if self.raffle.progress != Raffle.PROGRESS_CHOICES[1][0]:
            error_dict['raffle'].append(f'진행 상황이 <{self.raffle.get_progress_display()}>인 래플은 응모할 수 없습니다.')

        if len(error_dict) > 0:
            raise ValidationError(error_dict)

        super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 래플이 목표 수량을 채운 경우
        if self.raffle.applied_count == self.raffle.target_quantity:
            # 래플의 진행 상황을 종료(done)로 변경
            self.raffle.progress = Raffle.PROGRESS_CHOICES[2][0]  # done

            # 래플의 발표일시 업데이트
            self.raffle.announce_date_time = self.raffle.calc_announce_date_time(done_date_time=datetime.now())

            self.raffle.save(update_fields=['progress', 'announce_date_time'])

            # 1차 추첨 시작
            self.raffle.create_candidates()


class RaffleCandidate(models.Model):
    raffle_apply = models.OneToOneField(
        RaffleApply,
        verbose_name='1차 당첨',
        related_name='candidate',
        on_delete=models.CASCADE,
    )
    given_numbers = models.CharField(
        verbose_name='부여받은 번호',
        max_length=100,
    )

    class Meta:
        db_table = '_'.join((__package__, 'raffle_candidate'))


class RaffleWinner(models.Model):
    raffle_candidate = models.OneToOneField(
        RaffleCandidate,
        verbose_name='최종 당첨',
        related_name='winner',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = '_'.join((__package__, 'raffle_winner'))


class Lotto(models.Model):
    draw_no = models.SmallIntegerField(
        verbose_name='회차 번호',
        editable=False,
    )
    draw_date = models.DateField(
        verbose_name='추첨 날짜',
        unique=True
    )
    bonus_num = models.SmallIntegerField(
        verbose_name='보너스 당첨 번호',
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.draw_date.weekday() != 5:
            raise ValidationError({'draw_date': '토요일만 입력 가능합니다.'})
        if self.draw_date > datetime.now().date():
            raise ValidationError({'draw_date': '아직 로또 추첨이 진행되지 않았습니다.'})

        super().clean()

    def save(self, *args, **kwargs):
        self.clean()

        self.draw_no = self.__calc_lotto_no()
        self.bonus_num = self.__get_lotto_bonus_num()

        # super().save(*args, **kwargs)

        # 응모 종료('done') 상태이고 발표일이 동일한 래플들 추첨 진행하기
        qs = Raffle.objects.filter(
            progress=Raffle.PROGRESS_CHOICES[2][0],
            announce_date_time__date=self.draw_date
        )
        for raffle in qs:
            candidate_winner = raffle.candidates.get(given_numbers__contains=self.bonus_num)
            rw = RaffleWinner(raffle_candidate=candidate_winner)
            rw.save()

    def __calc_lotto_no(self):
        """
        date의 회차 번호 구하기
        """
        _first_draw_no = 1
        _first_draw_date = datetime(year=2002, month=12, day=7).date()  # '2002-12-07'
        # _draw_date_format = '%Y-%m-%d'

        return ((self.draw_date - _first_draw_date) / 7).days + 1

    def __get_lotto_bonus_num(self):
        lotto_api_url = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo='
        draw_no = self.__calc_lotto_no()

        res = requests.get(lotto_api_url + str(draw_no))
        return res.json().get('bnusNo', 0)
