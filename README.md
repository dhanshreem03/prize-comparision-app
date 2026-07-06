# Prize Comparison App

A Flask-based web application that compares product prices across multiple e-commerce platforms (Amazon, Flipkart, etc.). This app helps users find the best deals by scraping and comparing prices from different sources.

## Features

- 🔍 Search products across multiple platforms
- 💰 Compare prices from Amazon, Flipkart, and more
- 📊 View price differences and discounts
- 💾 Save product information to database
- 🖼️ Product images and details
- 👥 User authentication (coming soon)

## Project Structure

```
prize-comparision-app/
├── ScraperEngine/           # Web scraping module
│   ├── __init__.py
│   ├── base_scraper.py      # Abstract base class for all scrapers
│   ├── amazon_scraper.py    # Amazon India scraper
│   └── flipkart_scraper.py  # Flipkart scraper
├── module/                  # Application modules
│   ├── models.py            # Database models
│   └── __init__.py
├── static/                  # Static files (CSS, JS, images)
│   └── asset/
│       └── logo-1.png
├── template/                # HTML templates
│   ├── homescreen.html
│   ├── index.html
│   ├── login.html
│   ├── page.html
│   ├── productdetails.html
│   ├── register.html
│   └── searchresult.html
├── main.py                  # Flask application entry point
├── test.py                  # Test file for scrapers
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.11 or higher
- pip or poetry

### Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd prize-comparision-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```
   
   Or with poetry:
   ```bash
   poetry install
   ```

3. **Run the Flask application:**
   ```bash
   python main.py
   ```
   
   The app will be available at `http://127.0.0.1:8000`

## Usage

### Testing Scrapers

Run the test file to test the scrapers:
```bash
python test.py
```

This will scrape product information from Amazon and Flipkart for "IPHONE 16".

### API Endpoints

- `GET /` - Home page
- `POST /api/search` - Search for products (coming soon)
- `GET /api/products` - Get all products (coming soon)
- `POST /api/login` - User login (coming soon)
- `POST /api/register` - User registration (coming soon)

## Dependencies

- **flask>=3.1.3** - Web framework
- **flask-sqlalchemy>=3.1.1** - ORM for database
- **playwright>=1.61.0** - Web scraping browser automation

## Database

The app uses SQLAlchemy with SQLite by default. Database models include:
- `Product` - Stores scraped product information
- `User` - User accounts (for future features)

## Scrapers

### BaseScraper
Abstract base class that all scrapers inherit from. Provides common functionality like:
- Browser automation with Playwright
- Screenshot capture
- Error handling

### AmazonScraper
Scrapes products from Amazon India (amazon.in).

### FlipkartScraper
Scrapes products from Flipkart India.

## Contributing

Feel free to add more scrapers by extending the `BaseScraper` class.

## License

This project is open source and available for personal use.

## Future Enhancements

- User authentication system
- Wishlist functionality
- Price tracking over time
- More e-commerce platforms (eBay, Myntra, etc.)
- REST API endpoints
- Frontend improvements
