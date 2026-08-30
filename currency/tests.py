from django.test import TestCase
from unittest.mock import patch, MagicMock
from .models import ExchangeRate
from .utils import update_usd_rate


class ExchangeRateModelTests(TestCase):
    def test_create_exchange_rate(self):
        rate = ExchangeRate.objects.create(currency='USD', rate=41.5)
        self.assertEqual(rate.currency, 'USD')
        self.assertEqual(rate.rate, 41.5)

    def test_str_representation(self):
        rate = ExchangeRate.objects.create(currency='USD', rate=41.5)
        self.assertIn('USD', str(rate))
        self.assertIn('41.5', str(rate))

    def test_default_currency_is_usd(self):
        rate = ExchangeRate.objects.create(rate=41.5)
        self.assertEqual(rate.currency, 'USD')

    def test_ordering_is_by_most_recent(self):
        ExchangeRate.objects.create(currency='USD', rate=40.0)
        rates = list(ExchangeRate.objects.all())
        self.assertEqual(len(rates), 2)


class UpdateUsdRateTests(TestCase):
    """Tests for update_usd_rate() using mocked API responses - we
    don't want tests hitting the real NBU API (slow, unreliable,
    and not something a test suite should depend on).
    """

    @patch('currency.utils.requests.get')
    def test_update_usd_rate_creates_new_record(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{'rate': 41.75}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        update_usd_rate()

        self.assertTrue(ExchangeRate.objects.filter(currency='USD').exists())
        self.assertEqual(ExchangeRate.objects.get(currency='USD').rate, 41.75)

    @patch('currency.utils.requests.get')
    def test_update_usd_rate_updates_existing_record(self, mock_get):
        ExchangeRate.objects.create(currency='USD', rate=40.0)

        mock_response = MagicMock()
        mock_response.json.return_value = [{'rate': 42.0}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        update_usd_rate()

        # update_or_create should update the existing row, not add a second one
        self.assertEqual(ExchangeRate.objects.filter(currency='USD').count(), 1)
        self.assertEqual(ExchangeRate.objects.get(currency='USD').rate, 42.0)

    @patch('currency.utils.requests.get')
    def test_update_usd_rate_handles_api_failure_gracefully(self, mock_get):
        mock_get.side_effect = Exception("Connection failed")

        # Should not raise - the function catches its own exceptions
        try:
            update_usd_rate()
        except Exception:
            self.fail("update_usd_rate() should not propagate exceptions")

        self.assertFalse(ExchangeRate.objects.exists())