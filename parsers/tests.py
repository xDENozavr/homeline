from django.test import TestCase
from unittest.mock import patch
from announcements.models import Announcement
from parsers.services import save_announcement
from parsers.utils import run_all_parsers


SAMPLE_LISTING = {
    'announcement_title': '2-room apartment, 45 m2',
    'district': 'Metalurhiinyi District',
    'street': 'Shevchenka St.',
    'price': 25000,
    'rooms': '2',
    'meters': 45.0,
    'content': 'Nice apartment, recently renovated.',
    'images': ['https://example.com/photo1.jpg'],
    'floor': '3 / 9',
    'seller_name': 'Test Seller',
    'phone': '+380000000000',
    'link': 'https://rieltor.ua/some-listing-1',
}


class SaveAnnouncementTests(TestCase):
    def test_saves_new_announcement(self):
        result = save_announcement(SAMPLE_LISTING)
        self.assertTrue(result)
        self.assertTrue(Announcement.objects.filter(link=SAMPLE_LISTING['link']).exists())

    def test_does_not_duplicate_existing_link(self):
        save_announcement(SAMPLE_LISTING)
        result = save_announcement(SAMPLE_LISTING)
        self.assertFalse(result)
        self.assertEqual(Announcement.objects.filter(link=SAMPLE_LISTING['link']).count(), 1)

    def test_missing_required_field_fails_gracefully(self):
        broken_listing = SAMPLE_LISTING.copy()
        del broken_listing['price']
        result = save_announcement(broken_listing)
        self.assertFalse(result)
        self.assertFalse(Announcement.objects.filter(link=SAMPLE_LISTING['link']).exists())


class RunAllParsersTests(TestCase):

    # Patched at 'parsers.rieltor_parser.run_parser_rieltor', not
    # 'parsers.utils.run_parser_rieltor' - run_all_parsers() imports
    # run_parser_rieltor() INSIDE the function body (a local, dynamic
    # import, see utils.py), so the name only ever exists as an
    # attribute of the module where it's actually defined
    # (parsers.rieltor_parser). Patching the other path fails with
    # "module has no attribute 'run_parser_rieltor'".
    @patch('parsers.rieltor_parser.run_parser_rieltor')
    def test_removes_listings_not_returned_by_parser(self, mock_parser):
        stale = Announcement.objects.create(
            announcement_title='Old listing', district='X', street='Y',
            price=10000, rooms='1', meters=30.0, floor='1 / 5',
            link='https://rieltor.ua/stale-listing',
        )
        active_link = 'https://rieltor.ua/active-listing'
        Announcement.objects.create(
            announcement_title='Active listing', district='X', street='Y',
            price=20000, rooms='2', meters=40.0, floor='2 / 5',
            link=active_link,
        )

        mock_parser.return_value = {active_link}

        result = run_all_parsers()

        self.assertFalse(Announcement.objects.filter(pk=stale.pk).exists())
        self.assertTrue(Announcement.objects.filter(link=active_link).exists())
        self.assertEqual(result, {active_link})

    @patch('parsers.rieltor_parser.run_parser_rieltor')
    def test_does_not_crash_when_parser_returns_empty_set(self, mock_parser):
        mock_parser.return_value = set()

        try:
            run_all_parsers()
        except TypeError:
            self.fail("run_all_parsers() should handle a set return value without error")