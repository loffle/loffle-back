from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


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
