from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Announcement, Favorite
from currency.models import ExchangeRate

User = get_user_model()


def make_announcement(**overrides):
    defaults = {
        'announcement_title': '2-room apartment',
        'district': 'Metalurhiinyi District',
        'street': 'Shevchenka St.',
        'price': 25000,
        'rooms': '2',
        'meters': 45.0,
        'floor': '3 / 9',
        'link': 'https://rieltor.ua/listing-1',
    }
    defaults.update(overrides)
    return Announcement.objects.create(**defaults)


class AnnouncementModelTests(TestCase):
    def test_str_returns_title(self):
        an = make_announcement(announcement_title='Nice flat')
        self.assertEqual(str(an), 'Nice flat')

    def test_price_uah_uses_current_exchange_rate(self):
        ExchangeRate.objects.create(currency='USD', rate=41.0)
        an = make_announcement(price=1000)
        self.assertEqual(an.price_uah, 41000.0)

    def test_price_uah_falls_back_to_40_when_no_rate_exists(self):
        an = make_announcement(price=1000)
        self.assertEqual(an.price_uah, 40000.0)

    def test_price_uah_empty_when_price_is_zero(self):
        an = make_announcement(price=0)
        self.assertEqual(an.price_uah, "")


class FavoriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.announcement = make_announcement()

    def test_create_favorite(self):
        fav = Favorite.objects.create(user=self.user, announcement=self.announcement)
        self.assertEqual(fav.user, self.user)
        self.assertEqual(fav.announcement, self.announcement)

    def test_cannot_favorite_same_listing_twice(self):
        from django.db import IntegrityError
        Favorite.objects.create(user=self.user, announcement=self.announcement)
        with self.assertRaises(IntegrityError):
            Favorite.objects.create(user=self.user, announcement=self.announcement)


class ApartmentsViewTests(TestCase):
    def setUp(self):
        make_announcement(district='Metalurhiinyi District', street='Shevchenka St.', price=5000, rooms='1', meters=20.0, link='https://a.com/1')
        make_announcement(district='Saksahanskyi District', street='Sobornosti St.', price=35000, rooms='2', meters=45.0, link='https://a.com/2')
        make_announcement(district='Pokrovskyi District', street='Karla Marksa St.', price=150000, rooms='4', meters=90.0, link='https://a.com/3')

    def test_page_loads_with_all_listings(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 3)

    def test_filter_by_location(self):
        response = self.client.get(reverse('home'), {'location': 'Saksahanskyi'})
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_filter_by_price_range(self):
        response = self.client.get(reverse('home'), {'price_range': 'up_to_10000'})
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_filter_by_rooms(self):
        response = self.client.get(reverse('home'), {'rooms': '2'})
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_filter_by_meters_range(self):
        response = self.client.get(reverse('home'), {'meters_range': 'over_75met'})
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_combined_filters(self):
        response = self.client.get(reverse('home'), {'price_range': 'from10000_to40000', 'rooms': '2'})
        self.assertEqual(response.context['page_obj'].paginator.count, 1)


class AnnouncementDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.an = make_announcement(price=1000, meters=50.0, street='Shevchenka St.')

    def test_page_loads(self):
        response = self.client.get(reverse('announcement', args=[self.an.id]))
        self.assertEqual(response.status_code, 200)

    def test_404_for_nonexistent_listing(self):
        response = self.client.get(reverse('announcement', args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_is_favorited_false_for_anonymous_user(self):
        response = self.client.get(reverse('announcement', args=[self.an.id]))
        self.assertFalse(response.context['is_favorited'])

    def test_is_favorited_true_when_in_favorites(self):
        Favorite.objects.create(user=self.user, announcement=self.an)
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('announcement', args=[self.an.id]))
        self.assertTrue(response.context['is_favorited'])

    def test_potential_offer_flagged_when_price_much_lower_than_street_average(self):
        make_announcement(street='Shevchenka St.', price=5000, meters=50.0)
        response = self.client.get(reverse('announcement', args=[self.an.id]))
        self.assertTrue(response.context['is_potential_offer'])


class FavoriteAnnouncementViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.an = make_announcement()

    def test_requires_login(self):
        response = self.client.post(reverse('favorite_announcement'), {'an_id': self.an.id})
        self.assertNotEqual(response.status_code, 200)

    def test_requires_post(self):
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('favorite_announcement'))
        self.assertEqual(response.status_code, 405)

    def test_adds_to_favorites(self):
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.post(reverse('favorite_announcement'), {'an_id': self.an.id})
        self.assertEqual(response.json()['action'], 'added')
        self.assertTrue(Favorite.objects.filter(user=self.user, announcement=self.an).exists())

    def test_removes_from_favorites_on_second_click(self):
        self.client.login(username='testuser', password='StrongPass123!')
        self.client.post(reverse('favorite_announcement'), {'an_id': self.an.id})
        response = self.client.post(reverse('favorite_announcement'), {'an_id': self.an.id})
        self.assertEqual(response.json()['action'], 'removed')
        self.assertFalse(Favorite.objects.filter(user=self.user, announcement=self.an).exists())


class FavoritesListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.other_user = User.objects.create_user(username='otheruser', password='StrongPass123!')
        self.an1 = make_announcement(link='https://a.com/1')
        self.an2 = make_announcement(link='https://a.com/2')

    def test_requires_login(self):
        response = self.client.get(reverse('favorites_list'))
        self.assertNotEqual(response.status_code, 200)

    def test_shows_only_current_users_favorites(self):
        Favorite.objects.create(user=self.user, announcement=self.an1)
        Favorite.objects.create(user=self.other_user, announcement=self.an2)

        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('favorites_list'))

        favorites = response.context['favorites']
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0].announcement, self.an1)


class GetPhoneViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.an = make_announcement(phone='+380501234567')

    def test_requires_login(self):
        response = self.client.get(reverse('get_phone'), {'an_id': self.an.id})
        self.assertNotEqual(response.status_code, 200)

    def test_returns_phone_number(self):
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('get_phone'), {'an_id': self.an.id})
        self.assertEqual(response.json()['phone'], '+380501234567')


class GetDetailsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.an = make_announcement(announcement_title='Cozy flat', price=30000)

    def test_returns_listing_details(self):
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('get_details'), {'an_id': self.an.id})
        data = response.json()
        self.assertEqual(data['title'], 'Cozy flat')
        self.assertEqual(data['price'], 30000)

    def test_404_for_nonexistent_listing(self):
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('get_details'), {'an_id': 99999})
        self.assertEqual(response.status_code, 404)