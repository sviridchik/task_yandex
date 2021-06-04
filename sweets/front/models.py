from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from django.contrib.contenttypes import *
from django.db.models import CASCADE
from django.contrib.auth.models import User
from posts.models import Couriers


class Person(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    age = models.IntegerField("Возраст")
    gender_choce = [
        ("definite", (("w", "woman"),
                      ("m", "man"),
                      )),
        ("indefinite", (("t", "trans"),
                        ("o", "other"),))
    ]
    gender = models.CharField(max_length=100, choices=gender_choce, verbose_name="Пол", null=True, blank=True)
    email = models.CharField(max_length=255, verbose_name="email", default='')
    phone = models.CharField(max_length=255, verbose_name="телефон", default='', blank=True)
    user = models.ForeignKey('auth.User', verbose_name='Пользователь', on_delete=models.CASCADE)
    courier = models.OneToOneField(Couriers, verbose_name='Курьер', on_delete=models.CASCADE)
