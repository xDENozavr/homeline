from django.db import models

class ExchangeRate(models.Model):
    currency = models.CharField(max_length=10, default='USD')
    rate = models.FloatField()
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.currency}: {self.rate} UAH (updated {self.updated_at})"

    class Meta:
        ordering = ['-updated_at']