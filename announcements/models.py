from django.db import models
from django.conf import settings
from currency.models import ExchangeRate


class Announcement(models.Model):
    announcement_title = models.CharField(max_length=200, verbose_name="title")
    district = models.CharField(max_length=100, verbose_name="district")
    street = models.CharField(max_length=100, verbose_name="street")
    price = models.IntegerField(verbose_name="price ($)")
    rooms = models.CharField(max_length=10, verbose_name="rooms")
    meters = models.FloatField(verbose_name="area (m²)")
    content = models.TextField(blank=True, verbose_name="content")
    images = models.JSONField(default=list, verbose_name="photos")
    floor = models.CharField(max_length=30, verbose_name="floor")
    seller_name = models.CharField(max_length=100, blank=True, verbose_name="seller name")
    phone = models.CharField(max_length=70, blank=True, verbose_name="phone")
    link = models.URLField(blank=True, verbose_name="link")

    def __str__(self):
        return self.announcement_title

    @property
    def price_uah(self):
        """Converts the listing's USD price to UAH using the most
            recent exchange rate on record. Falls back to a fixed rate of
            40 if no ExchangeRate row exists yet (e.g. right after a fresh
            deploy, before update_usd_rate() has run for the first time).

            Uses an explicit order_by('-updated_at').first() rather than
            .last() - relying on .last() would silently depend on
            ExchangeRate.Meta.ordering matching what we want here, and
            would start returning the OLDEST rate instead of the newest
            if that ordering ever changed. See currency/models.py.
        """
        if not self.price:
            return ""
        current_rate = ExchangeRate.objects.filter(currency='USD').order_by('-updated_at').first()
        price_in_uah = self.price * (current_rate.rate if current_rate else 40)
        return round(price_in_uah, 2)

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"

Announcement.price_uah.fget.short_description = "Price (₴)"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents the same user from favoriting the same listing
        # twice - enforced at the database level, not just in the
        # view (see favorite_announcement in views.py, which relies
        # on get_or_create() to toggle add/remove instead of ever
        # trying to insert a genuine duplicate).
        unique_together = ('user', 'announcement')