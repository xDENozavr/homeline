import requests
from .models import ExchangeRate


def update_usd_rate():
    """Fetches the current USD exchange rate from the official NBU
    (National Bank of Ukraine) API and saves it to ExchangeRate."""

    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json"
    try:
        # Request to the NBU API
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        usd_rate = data[0]['rate']

        # Update the existing USD record, or create one if it doesn't exist yet
        ExchangeRate.objects.update_or_create(
            currency='USD',
            defaults={'rate': usd_rate}
        )
        # NOTE: print() here only shows up in the server console, not
        # to the actual user.
        print(f"USD rate updated: {usd_rate} UAH")
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")