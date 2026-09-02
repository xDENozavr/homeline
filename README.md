# HomeLine

A real estate listing aggregator for Kryvyi Rih, Ukraine, built with Django and PostgreSQL. Originally developed as a university thesis project, rebuilt from the ground up as a portfolio-ready application.

**Live demo:** https://homeline.onrender.com
**Note:** hosted on Render's free tier - the app may take up to 50 seconds to wake up on the first request after a period of inactivity. Listing photos are placeholder images (picsum.photos), not real property photos.

## Features

- Listing search and filtering by location, price range, room count, and area
- Favorites system for registered users
- Per-listing analytics: average price per m² by district/street, with a "potential good deal" indicator for listings priced well below the local average
- USD/UAH price conversion using a live exchange rate fetched from the National Bank of Ukraine API
- Custom admin panel with one-click actions to update the exchange rate or run the listing scraper
- A Selenium/BeautifulSoup scraper (`parsers` app) that collects listings from a real estate site - included as a demonstration of web scraping; the live demo uses synthetic data instead of real scraped listings
- Mobile-responsive design across all pages

## Tech stack

- **Backend:** Python, Django
- **Database:** PostgreSQL (via Django ORM)
- **Frontend:** HTML/CSS, vanilla JavaScript
- **Scraping:** Selenium, BeautifulSoup
- **Media storage:** Cloudinary (production)
- **Static files:** WhiteNoise
- **Testing:** Django TestCase
- **Deployment:** Render

## Running locally

```bash
git clone https://github.com/xDENozavr/homeline.git
cd homeline
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=homeline_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

Then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Project structure

```
announcements/  - listings, favorites, analytics
currency/       - USD/UAH exchange rate tracking
pages/          - static informational pages (FAQ, terms, about)
parsers/        - the web scraper (rieltor.ua)
users/          - authentication, user accounts
config/         - project settings, URL routing
```

## About this project

Built as a personal portfolio project to practice Django fundamentals: query optimization (`select_related`/`annotate`), form/model validation, admin customization, and integrating external services (scraping, third-party APIs).
