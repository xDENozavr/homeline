from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registration/', views.RegisterUser.as_view(), name='registration'),
    path('profile/', views.profile, name='profile'),
]