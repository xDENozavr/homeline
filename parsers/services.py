from announcements.models import Announcement


def save_announcement(apartments_info):
    """Adds a listing to the database if it doesn't already exist.

    Returns True if a new listing was created, False if it was a
    duplicate (by link) or if the data was invalid in some way (e.g.
    a required field missing from apartments_info) - callers use this
    boolean just to count new listings, not to distinguish between
    "duplicate" and "failed to save".
    """
    if Announcement.objects.filter(link=apartments_info['link']).exists():
        return False
    try:
        an = Announcement(
            announcement_title=apartments_info['announcement_title'],
            district=apartments_info['district'],
            street=apartments_info['street'],
            price=apartments_info['price'],
            rooms=apartments_info['rooms'],
            meters=apartments_info['meters'],
            content=apartments_info['content'],
            images=apartments_info['images'],
            floor=apartments_info['floor'],
            seller_name=apartments_info['seller_name'],
            phone=apartments_info['phone'],
            link=apartments_info['link'],
        )
        an.save()
        return True
    except Exception:
        return False