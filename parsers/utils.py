from announcements.models import Announcement


def run_all_parsers():
    """Runs every scraper, then removes any listing from the database
    whose link wasn't seen in this run - meaning it's no longer active
    on the source site(s). Returns the combined set of active links
    across all parsers.
    """
    from parsers.rieltor_parser import run_parser_rieltor

    actual_links = set()

    links_rieltor = run_parser_rieltor()

    actual_links.update(links_rieltor)

    # Anything currently stored whose link ISN'T in actual_links is no
    # longer live on the source site(s), so it's removed. This is why
    # run_parser_rieltor() returns the full set of links it saw this
    # run (including duplicates it skipped) rather than just the new
    # ones - a still-active listing that already existed in the
    # database would otherwise get deleted here by mistake.
    Announcement.objects.exclude(link__in=actual_links).delete()

    return actual_links