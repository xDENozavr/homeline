from .models import Announcement, Favorite
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Avg, F, ExpressionWrapper, FloatField

def apartments(request):
    location = request.GET.get('location')
    price_range = request.GET.get('price_range')
    rooms = request.GET.get('rooms')
    meters_range = request.GET.get('meters_range')

    an = Announcement.objects.all()

    if location:
        an = an.filter(Q(district__icontains=location) | Q(street__icontains=location))

    if price_range:
        if price_range == 'up_to_10000':
            an = an.filter(price__lte=10000)
        elif price_range == 'from10000_to40000':
            an = an.filter(price__gt=10000, price__lte=40000)
        elif price_range == 'from40000_to100000':
            an = an.filter(price__gt=40000, price__lte=100000)
        elif price_range == 'over_100000':
            an = an.filter(price__gt=100000)

    if rooms and rooms.isdigit():
        an = an.filter(rooms=int(rooms))

    if meters_range:
        if meters_range == 'up_to25met':
            an = an.filter(meters__lte=25)
        elif meters_range == 'from25met_to40met':
            an = an.filter(meters__gt=25, meters__lte=40)
        elif meters_range == 'from40met_to75met':
            an = an.filter(meters__gt=40, meters__lte=75)
        elif meters_range == 'over_75met':
            an = an.filter(meters__gt=75)

    paginator = Paginator(an, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    homeline_rows = [
        page_obj.object_list[i:i + 4]
        for i in range(0, len(page_obj.object_list), 4)
    ]

    return render(request, 'announcements/index.html', {
        'homeline_rows': homeline_rows,
        'page_obj': page_obj,
        'filters': {
            'location': location,
            'rooms': rooms,
            'price_range': price_range,
            'meters_range': meters_range,
        }
    })


def announcement(request, an_id):

    an = get_object_or_404(Announcement, id=an_id)

    price_uah = an.price_uah

    current_m2 = an.price / an.meters if an.meters else 0

    qs = Announcement.objects.annotate(
        price_per_m2=ExpressionWrapper(F('price') / F('meters'), output_field=FloatField())).filter(street=an.street)
    avg_price_m2 = qs.aggregate(avg=Avg('price_per_m2'))['avg'] or 0

    diff_percent = round(abs((current_m2 - avg_price_m2) / avg_price_m2 * 100), 2) if avg_price_m2 else 0

    price_direction = 'more expensive' if current_m2 > avg_price_m2 else 'cheaper'

    is_potential_offer = (price_direction == 'cheaper' and diff_percent >= 20)

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, announcement=an).exists()

    return render(request, 'announcements/announcement.html', {
        'an': an,
        'price_uah': price_uah,
        'diff_percent': diff_percent,
        'price_direction': price_direction,
        'is_potential_offer': is_potential_offer,
        'is_favorited': is_favorited,
    })


@login_required
@require_POST
def favorite_announcement(request):
    an_id = request.POST.get('an_id')
    announcement = get_object_or_404(Announcement, id=an_id)

    fav, created = Favorite.objects.get_or_create(user=request.user, announcement=announcement)
    if not created:
        fav.delete()
        action = 'removed'
    else:
        action = 'added'

    return JsonResponse({'status': 'ok', 'action': action})


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('announcement')
    return render(request, 'announcements/favorites.html', {'favorites': favorites})




def apartments(request):
    """Home page with listings, filtering, and pagination"""

    location = request.GET.get('location')
    price_range = request.GET.get('price_range')
    rooms = request.GET.get('rooms')
    meters_range = request.GET.get('meters_range')

    # order_by('-id') keeps pagination deterministic - without it,
    # Django/PostgreSQL don't guarantee a stable row order across
    # requests, so the same listing could reappear on a later page or
    # get skipped entirely as new rows are added between page loads.
    an = Announcement.objects.all().order_by('-id')

    if location:
        an = an.filter(Q(district__icontains=location) | Q(street__icontains=location))

    # Price/area filters use named range buckets from the frontend
    # (e.g. 'up_to_10000') rather than raw min/max query params
    if price_range:
        if price_range == 'up_to_10000':
            an = an.filter(price__lte=10000)
        elif price_range == 'from10000_to40000':
            an = an.filter(price__gt=10000, price__lte=40000)
        elif price_range == 'from40000_to100000':
            an = an.filter(price__gt=40000, price__lte=100000)
        elif price_range == 'over_100000':
            an = an.filter(price__gt=100000)

    if rooms and rooms.isdigit():
        an = an.filter(rooms=int(rooms))

    if meters_range:
        if meters_range == 'up_to25met':
            an = an.filter(meters__lte=25)
        elif meters_range == 'from25met_to40met':
            an = an.filter(meters__gt=25, meters__lte=40)
        elif meters_range == 'from40met_to75met':
            an = an.filter(meters__gt=40, meters__lte=75)
        elif meters_range == 'over_75met':
            an = an.filter(meters__gt=75)

    paginator = Paginator(an, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Groups the current page's listings into rows of 4 for the grid
    # layout, since the template just loops over rows rather than
    # doing the chunking itself.
    homeline_rows = [
        page_obj.object_list[i:i + 4]
        for i in range(0, len(page_obj.object_list), 4)
    ]

    return render(request, 'announcements/index.html', {
        'homeline_rows': homeline_rows,
        'page_obj': page_obj,
        'filters': {
            'location': location,
            'rooms': rooms,
            'price_range': price_range,
            'meters_range': meters_range,
        }
    })


def announcement(request, an_id):
    """Listing detail page with additional analytics"""

    an = get_object_or_404(Announcement, id=an_id)

    price_uah = an.price_uah

    current_m2 = an.price / an.meters if an.meters else 0

    # Average price per m² across all OTHER listings on the same
    # street - used below to flag unusually cheap listings as
    # potential good deals.
    qs = Announcement.objects.annotate(
        price_per_m2=ExpressionWrapper(F('price') / F('meters'), output_field=FloatField())).filter(street=an.street)
    avg_price_m2 = qs.aggregate(avg=Avg('price_per_m2'))['avg'] or 0

    diff_percent = round(abs((current_m2 - avg_price_m2) / avg_price_m2 * 100), 2) if avg_price_m2 else 0

    price_direction = 'more expensive' if current_m2 > avg_price_m2 else 'cheaper'

    # A listing is flagged as a "potential offer" if it's at least
    # 20% cheaper per m² than the street average - an arbitrary but
    # reasonable threshold for "worth a second look".
    is_potential_offer = (price_direction == 'cheaper' and diff_percent >= 20)

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, announcement=an).exists()

    return render(request, 'announcements/announcement.html', {
        'an': an,
        'price_uah': price_uah,
        'diff_percent': diff_percent,
        'price_direction': price_direction,
        'is_potential_offer': is_potential_offer,
        'is_favorited': is_favorited,
    })


@login_required
@require_POST
def favorite_announcement(request):
    """Adds or removes a listing from favorites (AJAX). Uses
    get_or_create() as a toggle: if the Favorite already existed,
    remove it; if it didn't, we just created it, so nothing more to
    do. This also means the unique_together constraint on Favorite
    (see models.py) never actually gets hit - we never try to create
    a genuine duplicate."""

    an_id = request.POST.get('an_id')
    announcement = get_object_or_404(Announcement, id=an_id)

    fav, created = Favorite.objects.get_or_create(user=request.user, announcement=announcement)
    if not created:
        fav.delete()
        action = 'removed'
    else:
        action = 'added'

    return JsonResponse({'status': 'ok', 'action': action})


@login_required
def favorites_list(request):
    """Shows all of the current user's favorited listings"""
    favorites = Favorite.objects.filter(user=request.user).select_related('announcement')
    return render(request, 'announcements/favorites.html', {'favorites': favorites})


def modal_apartment_photo(request, an_id):
    """Modal window for viewing an apartment's photos"""
    announcement = get_object_or_404(Announcement, id=an_id)
    return render(request, 'announcements/modal_apartment_photo.html', {
        'an': announcement,
        'images': announcement.images,
    })


def analytics(request):
    """Analytics across all listings"""
    base_qs = Announcement.objects.annotate(price_per_m2=ExpressionWrapper(F('price') / F('meters'), output_field=FloatField()))

    street_list = Announcement.objects.order_by('street').values_list('street', flat=True).distinct()

    current_street = request.GET.get('street', '').strip()
    if current_street:
        street_qs = base_qs.filter(street=current_street)
    else:
        street_qs = base_qs

    by_district = base_qs.values('district').annotate(avg_price=Avg('price_per_m2')).order_by('district')

    by_street = street_qs.values('street').annotate(avg_price=Avg('price_per_m2')).order_by('street')

    # ---- Room-count analytics ----
    # Both blocks below follow the same pattern: only run the query
    # if BOTH the location and room-count filters are actually set,
    # since a partial filter (e.g. district but no room count)
    # wouldn't produce a meaningful single number.
    current_room_district = request.GET.get('room_district', '').strip()
    current_room_count = request.GET.get('room_count', '').strip()
    room_count_district = 0
    avg_price_rooms_district = None

    if current_room_district and current_room_count:
        qs_rd = Announcement.objects.filter(district=current_room_district, rooms=current_room_count)
        room_count_district = qs_rd.count()
        avg_price_rooms_district = qs_rd.aggregate(avg=Avg('price'))['avg'] or 0

    current_room_street = request.GET.get('room_street', '').strip()
    current_room_count_street = request.GET.get('room_count_street', '').strip()
    room_count_street = 0
    avg_price_rooms_street = None

    if current_room_street and current_room_count_street:
        qs_rs = Announcement.objects.filter(street=current_room_street, rooms=current_room_count_street)
        room_count_street = qs_rs.count()
        avg_price_rooms_street = qs_rs.aggregate(avg=Avg('price'))['avg'] or 0

    return render(request, 'announcements/analytics.html', {
        'by_district': by_district,
        'by_street': by_street,
        'street_list': street_list,
        'current_street': current_street,
        'current_room_district': current_room_district,
        'current_room_count': current_room_count,
        'room_count_district': room_count_district,
        'avg_price_rooms_district': avg_price_rooms_district,
        'current_room_street': current_room_street,
        'current_room_count_street': current_room_count_street,
        'room_count_street': room_count_street,
        'avg_price_rooms_street': avg_price_rooms_street,
    })


@login_required
def get_phone(request):
    """Returns the seller's phone number for a given listing (AJAX)"""

    an_id = request.GET.get('an_id')
    an = get_object_or_404(Announcement, pk=an_id)
    phone = an.phone or ''
    return JsonResponse({'phone': phone})


@login_required
def get_details(request):
    """Returns listing details (title, price, description, etc.) as
    JSON (AJAX)."""

    an_id = request.GET.get('an_id')
    an = get_object_or_404(Announcement, pk=an_id)
    return JsonResponse({
        'title': an.announcement_title,
        'price': an.price,
        'content': an.content,
    })