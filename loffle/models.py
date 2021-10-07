from django.db import models

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


class Raffle(models.Model):
    begin_at = models.DateTimeField(
        verbose_name='응모 시작 날짜',
    )
    finish_at = models.DateTimeField(
        verbose_name='응모 종료 날짜',
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

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    objects = CommonManager()
    deleted_objects = CommonManager(is_deleted=True)


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
