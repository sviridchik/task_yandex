from sqlite3 import ProgrammingError

from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# Create your views here.


from .models import *
from .forms import RegistrForm
from django.contrib import messages


from django.shortcuts import render

def login_form(request, form):
    user = form.get_user()
    login(request, user)
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
    return render(request, 'auth.html', data)


def signup(request):
    data = {}
    if request.method == 'POST':
        form = RegistrForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(request, username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, "success")
            data['form'] = form
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
    return render(request, 'registr.html', data)