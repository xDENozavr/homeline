from django.urls import path
from . import views

urlpatterns = [
    path('terms/', views.terms_of_use, name = 'terms'),
    path('faq/', views.faq, name = 'faq'),
    path('about/', views.about_us, name = 'about'),
]