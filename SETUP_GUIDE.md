# Setup Guide for Prize Comparison App

## Quick Start

### Step 1: Install Dependencies

**Option A: Using pip with requirements.txt**
```bash
pip install -r requirements.txt
```

**Option B: Using pip with pyproject.toml**
```bash
pip install -e .
```

**Option C: Using poetry**
```bash
poetry install
```

### Step 2: Install Playwright Browsers

After installing dependencies, run:
```bash
playwright install
```

This downloads the browsers needed for web scraping.

### Step 3: Run the Flask Application

```bash
python main.py
```

The app will start at: **http://127.0.0.1:8000**

### Step 4: Test the Scrapers (Optional)

In another terminal, run:
```bash
python test.py
```

This will test the Amazon and Flipkart scrapers with "IPHONE 16" as the search term.

---

## Project Structure

```
prize-comparision-app/
├── ScraperEngine/              # Web scraping engine
│   ├── __init__.py
│   ├── base_scraper.py         # Base class for scrapers
│   ├── amazon_scraper.py       # Amazon India scraper
│   └── flipkart_scraper.py     # Flipkart scraper
├── module/                     # Application modules
│   ├── __init__.py
│   └── models.py               # Database models
├── static/                     # Static files
│   └── asset/
│       └── logo-1.png
├── template/                   # HTML templates
│   ├── index.html             # Main search page
│   ├── homescreen.html
│   ├── searchresult.html
│   ├── productdetails.html
│   ├── login.html
│   ├── register.html
│   └── page.html
├── main.py                     # Flask app entry point
├── test.py                     # Test file
├── config.py                   # Configuration
├── pyproject.toml             # Project metadata
├── requirements.txt           # Dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # Project readme
```

---

## API Endpoints

### Search Products
- **Endpoint:** `POST /api/search`
- **Request Body:**
  ```json
  {
    "product_name": "iPhone 16"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "product_name": "iPhone 16",
    "results": [...],
    "total": 10
  }
  ```

### Get All Products
- **Endpoint:** `GET /api/products`
- **Query Params:** `search_query=iPhone` (optional)
- **Response:**
  ```json
  {
    "success": true,
    "products": [...]
  }
  ```

### Get Product Details
- **Endpoint:** `GET /api/products/<product_id>`
- **Response:**
  ```json
  {
    "success": true,
    "product": {
      "id": 1,
      "product_name": "...",
      "source": "Amazon",
      ...
    }
  }
  ```

---

## Features Implemented

✅ Flask web server with database integration  
✅ Multi-platform scraping (Amazon, Flipkart)  
✅ Product comparison with pricing  
✅ Search API endpoint  
✅ Results storage in SQLite database  
✅ Modern, responsive UI  
✅ Real-time price comparison  

---

## Technologies Used

- **Backend:** Flask, Flask-SQLAlchemy
- **Scraping:** Playwright (headless browser automation)
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, Vanilla JavaScript

---

## Future Enhancements

- [ ] User authentication system
- [ ] Wishlist functionality
- [ ] Price tracking over time
- [ ] More e-commerce platforms (eBay, Myntra)
- [ ] Advanced filters and sorting
- [ ] Email notifications for price drops
- [ ] REST API documentation (Swagger)
- [ ] Mobile app version

---

## Troubleshooting

### Issue: Playwright browser not found
**Solution:** Run `playwright install`

### Issue: Database not creating
**Solution:** The database will be created automatically when you run the app for the first time

### Issue: Port 8000 already in use
**Solution:** Change the port in `main.py`:
```python
app.run(host='127.0.0.1', port=8001, debug=True)
```

### Issue: Scrapers timeout
**Solution:** The scrapers have a 60-second timeout. This is normal for first-time runs. Consider increasing if needed in `config.py`:
```python
SCRAPER_TIMEOUT = 90000  # 90 seconds
```

---

## Development Tips

1. **Hot Reload:** The app runs with `debug=True`, so changes are auto-reloaded
2. **Database:** SQLite file is created as `prize_comparison.db`
3. **Logging:** Check terminal output for scraper logs
4. **Testing:** Use `test.py` to verify scrapers work independently

---

## Contributing

To add a new scraper:

1. Create `new_platform_scraper.py` in `ScraperEngine/`
2. Inherit from `BaseScraper`
3. Implement required methods:
   - `site_name` property
   - `get_search_url()`
   - `parse_products()`
4. Update `ScraperEngine/__init__.py` to export it
5. Add to `main.py` search endpoint

Example:
```python
from .base_scraper import BaseScraper

class NewPlatformScraper(BaseScraper):
    @property
    def site_name(self) -> str:
        return "NewPlatform"
    
    def get_search_url(self, query: str) -> str:
        return f"https://example.com/search?q={query}"
    
    def parse_products(self, page):
        # Your parsing logic here
        return products
```

---

## License

Open source - Feel free to use and modify for personal projects.
