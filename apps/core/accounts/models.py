from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自訂使用者模型"""
    phone = models.CharField('電話號碼', max_length=20, blank=True)
    avatar = models.ImageField('頭像', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('個人簡介', blank=True)

    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者'
