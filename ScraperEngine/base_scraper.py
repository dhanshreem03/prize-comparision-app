"""Base Scraper class with common functionality for all scrapers."""
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Optional
from pathlib import Path
import time


class BaseScraper(ABC):
    """Abstract base class for all website scrapers."""

    def __init__(self, headless: bool = False, timeout: int = 60000, screenshot_session_folder: str = None):
        """
        Initialize the scraper.

        Args:
            headless: Run browser in headless mode (default: False for debugging)
            timeout: Page load timeout in milliseconds (default: 60000)
            screenshot_session_folder: Path to the session folder for storing screenshots
        """
        self.headless = headless
        self.timeout = timeout
        self.screenshot_session_folder = screenshot_session_folder
        self.screenshot_path = None  # Will store the path of the captured screenshot
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.viewport = {"width": 1920, "height": 1080}

    @property
    @abstractmethod
    def site_name(self) -> str:
        """Return the name of the website."""
        pass

    @abstractmethod
    def get_search_url(self, query: str) -> str:
        """Return the search URL for the given query."""
        pass

    @abstractmethod
    def parse_products(self, page: Page) -> list[dict]:
        """Parse products from the page and return list of product dictionaries."""
        pass

    def scrape(self, product_name: str) -> list[dict]:
        """
        Scrape products from the website.

        Args:
            product_name: The product to search for

        Returns:
            List of dictionaries containing:
            - product_name
            - price
            - discounted_price
            - image_url
            - product_url
            - source (website name)
            - screenshot_path (path to the screenshot)
        """
        query = product_name.replace(" ", "+")
        url = self.get_search_url(query)
        products = []
        self.screenshot_path = None  # Reset screenshot path for each scrape

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport=self.viewport
                )
                page = context.new_page()

                # Navigate to search page
                page.goto(url, wait_until="domcontentloaded",
                          timeout=self.timeout)

                # Wait for content to load
                self.wait_for_content(page)

                # Take screenshot if session folder is provided
                if self.screenshot_session_folder:
                    self.screenshot_path = self._take_screenshot(page)

                # Parse products
                products = self.parse_products(page)

                # Add source and screenshot_path to each product
                for product in products:
                    product["source"] = self.site_name
                    product["screenshot_path"] = self.screenshot_path if self.screenshot_path else ""

                browser.close()

        except Exception as e:
            print(f"[{self.site_name}] Error during scraping: {e}")

        print(f"[{self.site_name}] Found {len(products)} products")
        return products

    def _take_screenshot(self, page: Page) -> str:
        """
        Take a screenshot of the current page and save it.

        Args:
            page: Playwright page object

        Returns:
            Relative path to the saved screenshot
        """
        try:
            # Generate timestamp for filename
            timestamp = int(time.time())
            site_name_clean = self.site_name.lower().replace(" ", "_")
            filename = f"{timestamp}_{site_name_clean}.png"

            # Create full path
            screenshot_folder = Path(self.screenshot_session_folder)
            screenshot_folder.mkdir(parents=True, exist_ok=True)

            full_path = screenshot_folder / filename

            # Take screenshot
            page.screenshot(path=str(full_path), full_page=False)

            # Return relative path from workspace root
            relative_path = str(full_path).replace("\\", "/")
            print(f"[{self.site_name}] Screenshot saved: {relative_path}")
            return relative_path

        except Exception as e:
            print(f"[{self.site_name}] Error taking screenshot: {e}")
            return ""

        print(f"[{self.site_name}] Found {len(products)} products")
        return products

    def wait_for_content(self, page: Page, timeout: int = 10000):
        """Wait for page content to load. Override in subclasses if needed."""
        page.wait_for_timeout(3000)

    def safe_get_text(self, element) -> Optional[str]:
        """Safely get text from an element."""
        try:
            if element:
                return element.inner_text().strip()
        except:
            pass
        return None

    def safe_get_attribute(self, element, attr: str) -> Optional[str]:
        """Safely get attribute from an element."""
        try:
            if element:
                return element.get_attribute(attr)
        except:
            pass
        return None
