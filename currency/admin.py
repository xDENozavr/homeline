from django.contrib import admin
from .models import ExchangeRate

class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate', 'updated_at']
    list_filter = ['currency',]
    ordering = ['-updated_at',]

admin.site.register(ExchangeRate, ExchangeRateAdmin)