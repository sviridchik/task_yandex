from django import forms
# Подключаем компонент UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
# Подключаем модель User
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.forms import BaseForm

from .models import *
from posts.models import Couriers
import requests
from sweets.settings import API_HOST
import json

courier_type_ch = (
    ('foot', 'foot'),
    ('bike', 'bike'),
    ('car', 'car'),
)


class RegistrForm(UserCreationForm):
    # username = forms.CharField(blank=True, max_length=150, unique=True, )

    gender_choce = (
        ("definite", (("w", "woman"),
                      ("m", "man"),
                      )),
        ("indefinite", (("t", "trans"),
                        ("o", "other"),))
    )

    gender = forms.ChoiceField(choices=gender_choce, required=False)
    first_name = forms.CharField(label='Имя', max_length=70, required=False)
    last_name = forms.CharField(label='Фамилия', max_length=70, required=False)
    courier_type = forms.ChoiceField(label='Тип курьера', choices=courier_type_ch, help_text='This field is required')
    regions = forms.CharField(label='Регионы', max_length=255, help_text='This field is required')
    working_hours = forms.CharField(label='Рабочие часы', max_length=255, help_text='This field is required')
    email = forms.EmailField(label='Адрес E-mail', max_length=150, help_text='This field is required')
    phone = forms.CharField(label='Мобильный телефон', max_length=28, required=False)
    # password1 = forms.CharField(label='Пароль', max_length=128)
    # password2 = forms.CharField(label='Подтверждение пароля', max_length=128)
    age = forms.IntegerField(help_text='This field is required', min_value=0, max_value=120)

    def clean_age(self):
        if self.cleaned_data['age'] < 18:
            raise ValidationError('Нет 18 лет')
        return self.cleaned_data['age']

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        if (phone.startswith('+') and len(list(filter(lambda char: char.isdigit(), phone[1:]))) == len(
                phone) - 1) or len(phone) == 0:
            return self.cleaned_data['phone']
        else:
            raise ValidationError('Телефон в неправильном формате')

    class Meta:
        # Свойство модели User
        model = User
        # Свойство назначения полей
        fields = (
            'username', 'first_name', 'last_name', 'age', 'gender', 'email', 'phone', 'courier_type', 'regions',
            'working_hours',
            'password1', 'password2',)

    def save(self, commit=True):
        profiles = Couriers.objects.all().order_by('-courier_id')
        if len(profiles) == 0:
            courier_id = 0
        else:
            courier_id = profiles[0].courier_id + 1
        resp = requests.post(f'http://{API_HOST}:8000/posts/couriers', json={
            "data": [
                {
                    "courier_id": courier_id,
                    "courier_type": self.cleaned_data['courier_type'],
                    "regions": json.loads(self.cleaned_data['regions']),
                    "working_hours": json.loads(self.cleaned_data['working_hours'])
                }
            ]
        })
        if resp.ok:
            user = super().save(commit)

            person = Person.objects.create(
                **{
                    'title': self.cleaned_data['username'],
                    'age': self.cleaned_data['age'],
                    'gender': self.cleaned_data['gender'],
                    'email': self.cleaned_data['email'],
                    'phone': self.cleaned_data['phone'],
                    'user': user,
                    'courier': Couriers.objects.get(courier_id=courier_id)
                })
            return person
        else:
            raise ValidationError(resp.text)


class ContactForm(BaseForm):
    languages = forms.CharField(label='Имя (Необязательное поле)', max_length=255, required=False)
    vaccition = forms.EmailField(label='Email (Необязательное поле)', max_length=255, required=False)
    phone = forms.CharField(label='Опишите вашу проблему*', max_length=255, required=False)


class EditForm(forms.Form):
    courier_type = forms.ChoiceField(label='Тип курьера', choices=courier_type_ch)
    regions = forms.CharField(label='Регионы', max_length=255)
    working_hours = forms.CharField(label='Рабочие часы', max_length=255)
