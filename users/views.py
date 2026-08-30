from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterUserForm, LoginUserForm


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})