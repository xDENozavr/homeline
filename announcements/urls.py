from django.urls import path
from . import views

urlpatterns = [
    path('', views.apartments, name='home'),
    path('announcement/<int:an_id>/', views.announcement, name='announcement'),
    path('announcement/favorite/', views.favorite_announcement, name='favorite_announcement'),
    path('announcement/<int:an_id>/modal_apartment_photo/', views.modal_apartment_photo, name='modal_apartment_photo'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('analytics/', views.analytics, name='analytics'),
    path('get_phone/', views.get_phone, name='get_phone'),
    path('get_details/', views.get_details, name='get_details'),
]