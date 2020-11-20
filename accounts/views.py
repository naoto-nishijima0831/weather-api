from django.shortcuts import render, redirect

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import(LoginView, LogoutView)
from django.contrib.auth.models import User
from .forms import LoginForm

def index(request):
    if request.user.is_authenticated:
        return redirect('weatherview/')
    else:
        return redirect('login/')

class Login(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'


class Logout(LoginRequiredMixin, LogoutView):
    template_name = 'accounts/login.html'
