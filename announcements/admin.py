from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Announcement
from currency.utils import update_usd_rate
from parsers.utils import run_all_parsers


# Custom filter for searching by price range
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Price'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        """Price filter"""

        return (
            ('0-10000', 'Up to $10,000'),
            ('10000-40000', '$10,000 - $40,000'),
            ('40000-100000', '$40,000 - $100,000'),
            ('100000-', 'Over $100,000'),
        )

    def queryset(self, request, queryset):
        """Returns the listings queryset filtered by the selected price range"""

        value = self.value()
        if value:
            min_price, max_price = value.split('-')
            min_price = int(min_price)
            if max_price:
                max_price = int(max_price)
                return queryset.filter(price__gte=min_price, price__lte=max_price)
            else:
                return queryset.filter(price__gte=min_price)
        return queryset


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('announcement_title', 'district', 'price', 'price_uah', 'rooms', 'meters', 'floor', 'seller_name')
    list_filter = (PriceRangeFilter, 'rooms', 'district')
    search_fields = ('announcement_title', 'district', 'street', 'seller_name', 'price')
    readonly_fields = ('price_uah',)
    fieldsets = (
        ('Basic information', {
            'fields': ('announcement_title', 'district', 'street', 'price', 'price_uah', 'rooms', 'meters', 'floor')
        }),
        ('Seller & details', {
            'fields': ('seller_name', 'phone', 'content', 'link')
        }),
        ('Photos', {
            'fields': ('images',)
        }),
    )
    change_list_template = "admin/announcements/announcement_changelist.html"  # custom template with the extra action buttons

    def get_urls(self):
        # Adds two extra admin-only URLs (visible as buttons in the
        # changelist template above) so staff can trigger the exchange
        # rate update or the scraper directly from the admin UI,
        # without needing shell access.
        urls = super().get_urls()
        custom_urls = [
            path('run_update_usd/', self.admin_site.admin_view(self.run_update_usd), name='run_update_usd'),
            path('run_parser/', self.admin_site.admin_view(self.run_parser), name='run_parser'),
        ]
        return custom_urls + urls

    def run_update_usd(self, request):
        try:
            update_usd_rate()
            messages.success(request, "USD rate updated")
        except Exception as e:
            messages.error(request, f"Error fetching exchange rate: {str(e)}")
        return HttpResponseRedirect("../")

    def run_parser(self, request):
        # NOTE: this runs the Selenium scraper synchronously, inside
        # the request itself - the admin page (and the whole server,
        # since Django's dev server is single-threaded by default)
        # will block until scraping finishes, which can take minutes.
        try:
            run_all_parsers()
            messages.success(request, "Parsing completed successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred while running the parser: {str(e)}")
        return HttpResponseRedirect("../")

admin.site.register(Announcement, AnnouncementAdmin)