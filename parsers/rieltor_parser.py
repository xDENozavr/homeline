import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from currency.models import ExchangeRate
from parsers.services import save_announcement
import traceback

def get_current_usd_rate():
    """Returns the current USD→UAH rate, or a sane fallback if none
    is stored yet - matches the same fallback used in
    Announcement.price_uah (see announcements/models.py)."""
    current_rate = ExchangeRate.objects.filter(currency='USD').order_by('-updated_at').first()
    return current_rate.rate if current_rate else 40

def run_parser_rieltor():
    """
    Scrapes apartment listings from rieltor.ua and saves them to the
    database. Returns the set of links for every listing that was
    processed this run (both new and already-existing ones) - this is
    needed by run_all_parsers(), which uses it to figure out which
    listings are still active and delete the ones that aren't.
    """
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")  # hide automation from anti-bot detection

    driver = webdriver.Chrome(options=options)
    driver.get('https://rieltor.ua/krivoj-rog/flats-sale/?page=1#9.26/47.9195/33.3864')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    all_announcements_count = int(soup.find('span', attrs={'data-listing-count': True}).text.strip().split()[0])  # total listing count
    all_pages_count = (all_announcements_count // 20) + 1 if all_announcements_count % 20 != 0 else all_announcements_count // 20  # total page count

    added_count = 0
    collected_links = set()

    for page in range(1, all_pages_count + 1):
        print(f"Parsing page {page}...")

        driver.get(f'https://rieltor.ua/krivoj-rog/flats-sale/?page={page}#9.26/47.9195/33.3864')
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        current_page = soup.find_all(class_='catalog-card-media')
        if not current_page:
            print("No more pages with listings")
            break

        for announcement in range(len(current_page)):
            href = current_page[announcement].get('href')
            driver.get(href)
            time.sleep(1.5)
            html2 = driver.page_source
            main_soup = BeautifulSoup(html2, 'html.parser')
            apartments_info = {}

            try:
                count_class_name = len(main_soup.find_all(class_='address-link'))
                if count_class_name == 6:
                    apartments_info['announcement_title'] = main_soup.find_all(class_='address-link')[0].text + main_soup.find_all(class_='address-link')[0].next_sibling
                    apartments_info['street'] = main_soup.find_all(class_='address-link')[0].text
                else:
                    title = main_soup.find_all(class_='address-link')[2].next_sibling.split(',')
                    apartments_info['announcement_title'] = title[1] + ', ' + title[2]
                    street = main_soup.find_all(class_='address-link')[2].next_sibling.split(',')[1]
                    apartments_info['street'] = street

                price_text = main_soup.find(class_='offer-view-price-title').text.replace(' ', '').strip()
                if 'грн' in price_text:
                    uah_amount = int(price_text.replace('грн', ''))
                    usd_rate = get_current_usd_rate()
                    apartments_info['price'] = round(uah_amount / usd_rate)
                else:
                    apartments_info['price'] = int(price_text.replace('$', ''))

                district_link = main_soup.find(
                    'a', class_='address-link',
                    attrs={'data-analytics-event': 'card-click-region'}
                )
                apartments_info['district'] = district_link.text.strip(' р-н') if district_link else ''

                apartments_info['rooms'] = main_soup.find(class_='offer-view-details-column').find('a').text.split(' ')[0]
                apartments_info['meters'] = float(main_soup.find(class_='offer-view-details-column').find_all(class_='offer-view-details-row')[1].text.strip().split(' / ')[0])
                content_blocks = main_soup.find_all(class_='offer-view-section-text')
                apartments_info['content'] = " ".join(
                    [block.text.strip() for block in content_blocks]) if content_blocks else "No description available"
                apartments_info['images'] = [img.get('src') for img in main_soup.find_all(class_='offer-photo-gallery__image')]
                floor = main_soup.find(class_='offer-view-details-column').find_all(class_='offer-view-details-row')[2].text.strip()
                apartments_info['floor'] = f'{floor.split()[1]} / {floor.split()[3]}'
                apartments_info['seller_name'] = main_soup.find(class_='offer-view-rieltor-name').text.strip()
                apartments_info['phone'] = main_soup.find(class_='offer-view-rieltor-phones').text.strip()
                apartments_info['link'] = href
            except Exception as e:
                # Broad except is intentional here: a single malformed
                # listing page shouldn't crash the whole scraping run.
                # We log the full traceback and move on to the next
                # listing instead.
                print(f"Error collecting listing data ({href}): {e}")
                print("-" * 40)
                traceback.print_exc()  # prints the exact line where the error occurred
                print("-" * 40)
                continue

            # Track this link regardless of whether it was new or a
            # duplicate - run_all_parsers() needs the FULL set of
            # currently active listings, not just the new ones, to
            # correctly figure out which stored listings are stale.
            collected_links.add(apartments_info['link'])

            added = save_announcement(apartments_info)
            if not added:
                print(f"Listing {apartments_info['link']} already exists - skipping.")
            else:
                print("New listing:", apartments_info['link'])
                added_count += 1

    driver.quit()
    print(f"New listings added: {added_count}")
    return collected_links