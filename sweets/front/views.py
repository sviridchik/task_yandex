import logging
import threading
from sqlite3 import ProgrammingError

import requests
from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from rest_framework.authtoken.models import Token
import json

from sweets.settings import API_HOST, log_path, log_level, API_PORT
# Create your views here.

# from .models import *
from .forms import RegistrForm, EditForm, OrderAddForm
from django.contrib import messages

from django.shortcuts import render

logging.basicConfig(filename=log_path, level=getattr(logging, log_level))


# Create your views here.
def signin(request):
    data = {}
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # form.save()
            login_form(request, form)
            # user = form.get_user()
            # login(request, user)
            messages.success(request, "success")
            data['form'] = form

            # data['res'] = "Всё прошло успешно"
            return redirect('/home')
        else:
            data['form'] = form
            messages.error(request, "Неверный логин или пароль")
            # form = UserCreationForm()
            # return render(request, 'auth.html', data)
    else:
        form = AuthenticationForm()
        data['form'] = form
    return render(request, 'signin.html', data)


def signup(request):
    data = {}
    if request.method == 'POST':
        form = RegistrForm(request.POST)
        data['form'] = form
        if form.is_valid():
            try:
                form.save()
            except (ValidationError, json.JSONDecodeError) as e:
                messages.error(request, 'Ошибка в Регионах или в Рабочих часах')
            else:
                user = authenticate(request, username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
                login(request, user)
                messages.success(request, "success")
                # data['res'] = "Всё прошло успешно"
                return redirect('/home')
        else:
            data['form'] = form
            messages.error(request, 'Ошибка регистрации')
            # form = UserCreationForm()
            # return render(request, 'auth.html', data)
    else:
        form = RegistrForm()
        data['form'] = form
    return render(request, 'signup.html', data)


def start(request):
    return render(request, 'start.html', {'title': 'Start'})


def home(request):
    if not request.user.is_authenticated:
        return redirect('start')
    return render(request, 'home.html', {'title': 'Home'})


def work(request):
    if request.user.is_staff:
        return redirect('home')
    if not hasattr(request.user, 'person_set'):
        return redirect('signup')
    else:
        person = request.user.person_set.get()

        if request.method == 'POST':
            if 'get_new_orders' in request.GET:
                token, created = Token.objects.get_or_create(user=request.user)
                resp = requests.post(f'http://{API_HOST}:{API_PORT}/posts/orders/assign', json={
                    "courier_id": person.courier.courier_id,
                    'token': token.key,
                    'user_id': request.user.id
                })

                if not resp.ok:
                    logging.warning(f'Ошибка назначения заказов клиента {person}: {resp.text}')
                    logging.error(resp.text)
                    return redirect('work')

                result = resp.json()['orders']
                if len(result) == 0:
                    messages.warning(request, 'Для Вас подходящих заказов пока нет')
                else:
                    res = " ".join(map(str, result)).replace('\'', '')
                    messages.success(request, f'ID новых заказов: {res}')
                    logging.error(f'ID новых заказов: {res}')

            if 'complete_order' in request.GET:
                token, created = Token.objects.get_or_create(user=request.user)
                resp = requests.post(f'http://{API_HOST}:{API_PORT}/posts/orders/complete', json={
                    "courier_id": person.courier.courier_id,
                    "order_id": request.GET['complete_order'],
                    "complete_time": str(timezone.localtime().strftime('%Y-%m-%dT%H:%M:%S.%fZ')),
                    'token': token.key,
                    'user_id': request.user.id
                })
                if not resp.ok:

                    logging.warning(f'Ошибка завершения заказа клиента {person}: {resp.text}')
                    return redirect('work')
                else:
                    res = resp.text.replace('\"', '')
                    messages.success(request, res)

    token, created = Token.objects.get_or_create(user=request.user)
    resp = requests.get(f'http://{API_HOST}:{API_PORT}/posts/couriers/{person.courier.courier_id}', json={
        'token': token.key,
        'user_id': request.user.id
    })
    if not resp.ok:
        logging.warning(f'Ошибка получения курьера клиентом {person}: {resp.text}')
        return redirect('signup')
    else:
        context = resp.json()
        context['person'] = request.user.person_set.get()
        context['active_orders'] = person.courier.orders_set.filter(complete=False)
        return render(request, 'work.html', context)


def edit(request):
    current_courier = request.user.person_set.get().courier
    if request.method == 'POST':
        form = EditForm(data=request.POST)
        if form.is_valid():
            try:
                token, created = Token.objects.get_or_create(user=request.user)
                resp = requests.patch(f'http://{API_HOST}:{API_PORT}/posts/couriers/{current_courier.courier_id}',
                                      json={
                                          "courier_type": request.POST['courier_type'],
                                          "regions": json.loads(request.POST['regions']),
                                          "working_hours": json.loads(request.POST['working_hours']),
                                          'token': token.key,
                                          'user_id': request.user.id
                                      })
            except json.JSONDecodeError:
                messages.error(request, 'Введите правильный JSON формат')
                return render(request, 'edit.html', {'form': form})

            if resp.ok:
                messages.success(request, f'Профиль успешно отредактирован')
                return redirect('work')
            else:
                messages.error(request, resp.text)
                return render(request, 'edit.html', {'form': form})
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = EditForm(
            data={'courier_type': str(current_courier.courier_type), 'regions': str(current_courier.regions),
                  'working_hours': str(current_courier.working_hours).replace("'", '"')})
    return render(request, 'edit.html', {'form': form})


def contacts(request):
    if request.method == 'POST':
        thread = threading.Thread(target=send_mail, args=[
            f'Вопрос от клиента {request.POST["name"]}',
            f'''Почта клиента: {request.POST["email"]}
Вопрос клиента: {request.POST["message"]} ''',
            'avivasite007@gmail.com',
            ['viccisviri@gmail.com']],
                                  kwargs={'fail_silently': False})
        thread.start()
        messages.success(request, 'Ваше письмо отправлено, ожидайте ответа')

    return render(request, 'contacts.html')


def add_order(request):
    if not request.user.is_staff:
        raise Http404()

    if request.method == 'POST':
        form = OrderAddForm(data=request.POST)
        if form.is_valid():
            try:
                order = form.save()
            except json.JSONDecodeError:
                messages.error(request, 'Введите правильный JSON формат')
                return render(request, 'add_order.html', {'form': form})
            except ValidationError:
                messages.error(request, 'Некоторые данные введены неверно')
                return render(request, 'add_order.html', {'form': form})

            messages.success(request, f'Добавлен новый заказ с id {order.order_id}')
            form = OrderAddForm()
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = OrderAddForm()
    return render(request, 'add_order.html', {'form': form})
