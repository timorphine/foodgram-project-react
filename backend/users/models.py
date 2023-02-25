from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель User."""

    username = models.CharField(
        verbose_name='Логин пользователя',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()
