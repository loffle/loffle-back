from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Sum, Count, F, Q, FilteredRelation
from django.db.models.functions import Coalesce


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='이메일',
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        verbose_name='닉네임',
        max_length=24,
        unique=True,
    )
    sex = models.CharField(
        verbose_name='성별',
        max_length=1,
        choices=(
            ('M', '남자',),
            ('F', '여자',),
        ),
    )
    phone = models.CharField(
        verbose_name='핸드폰',
        max_length=11,
        unique=True,
    )

    last_name = None
    first_name = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'sex', 'phone']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.username

    @property
    def num_buy_tickets(self):
        return self.buy_tickets \
            .select_related('ticket') \
            .aggregate(num_buy_tickets=Coalesce(Sum(F('ticket__quantity')), 0))['num_buy_tickets']

    @property
    def num_use_tickets(self):
        return self.applied_raffles \
            .select_related('raffle') \
            .aggregate(num_use_tickets=Coalesce(Count(F('raffle_id')), 0))['num_use_tickets']

    # 돌려받는 티켓의 수량은 취소된 응모의 개수
    @property
    def num_return_tickets(self):
        return self.applied_raffles \
            .select_related('raffle') \
            .annotate(raffle_failed=FilteredRelation(
                        'raffle', condition=Q(raffle__progress='failed'))) \
            .aggregate(num_return_tickets=Coalesce(Count(F('raffle_failed')), 0))['num_return_tickets']

    # 사용자가 소유한 티켓 수량 = 구매한 티켓 수량 - 사용한 티켓 개수 + 응모한 래플이 취소되어 돌려받은 래플 개수
    @property
    def num_tickets(self):
        return self.num_buy_tickets - self.num_use_tickets + self.num_return_tickets
