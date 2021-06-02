from django import forms
# Подключаем компонент UserCreationForm
from django.contrib.auth.forms import UserCreationForm
# Подключаем модель User
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.forms import BaseForm

from sweets.posts.models import *


# Создаём класс формы
class RegistrForm(UserCreationForm):
    courier_type_ch = (
        ('foot', 'foot'),
        ('bike', 'bike'),
        ('car', 'car'),
    )
    # Добавляем новое поле Email

    courier_type = forms.CharField(max_length=255,choices=courier_type_ch,blank=False)
    regions = forms.CharField(max_length=255, blank=False)
    working_hours = models.CharField(max_length=255, blank=False)
    assign_time_current_for_delivery = models.DateTimeField(null=True)


    # def clean_age(self):
    #     if self.cleaned_data['age'] < 18:
    #         raise ValidationError('Нет 18 лет')
    #     return self.cleaned_data['age']
    #
    # def clean_phone(self):
    #     phone = self.cleaned_data['phone'].strip()
    #
    #     if (phone.startswith('+') and len(list(filter(lambda char: char.isdigit(), phone[1:]))) == len(
    #             phone) - 1) or len(phone) == 0:
    #         return self.cleaned_data['phone']
    #     else:
    #         raise ValidationError('Телефон в неправильном формате')

    # Создаём класс Meta
    class Meta:
        # Свойство модели User
        model = User
        # Свойство назначения полей
        fields = (
            'username', 'email', 'age', 'gender', 'family_name', 'amount_members', 'abilities', 'desease', 'phobias',
            'languages', 'vaccition', 'phone', 'password1', 'password2',)

    def save(self, commit=True):
        user = super().save(commit)
        User.objects.create(
            **{
                'title': self.cleaned_data['title'],
                'courier_type': self.cleaned_data['courier_type'],
                'regions': self.cleaned_data['regions'],
                'working_hours': self.cleaned_data['working_hours'],
                'user': user
            })


class ContactForm(BaseForm):
    languages = forms.CharField(label='Имя (Необязательное поле)', max_length=255, required=False)
    vaccition = forms.EmailField(label='Email (Необязательное поле)', max_length=255, required=False)
    phone = forms.CharField(label='Опишите вашу проблему*', max_length=255, required=False)
