"""Amazon India Scraper"""
from playwright.sync_api import Page
from .base_scraper import BaseScraper


class AmazonScraper(BaseScraper):
    """Scraper for Amazon India (amazon.in)"""

    @property
    def site_name(self) -> str:
        return "Amazon"

    def get_search_url(self, query: str) -> str:
        return f"https://www.amazon.in/s?k={query}"

    def wait_for_content(self, page: Page, timeout: int = 15000):
        """Wait for Amazon product cards to load."""
        try:
            page.wait_for_selector(
                'div[data-component-type="s-search-result"]', timeout=timeout)
        except:
            try:
                page.wait_for_selector('.s-result-item', timeout=timeout)
            except:
                pass
        page.wait_for_timeout(2000)

    def parse_products(self, page: Page) -> list[dict]:
        """Parse Amazon product cards."""
        products = []

        # Get all product cards
        product_cards = page.query_selector_all(
            'div[data-component-type="s-search-result"]')
        if not product_cards:
            product_cards = page.query_selector_all(
                '.s-result-item[data-asin]:not([data-asin=""])')

        for card in product_cards:
            try:
                asin = card.get_attribute('data-asin')
                if not asin:
                    continue

                # Product name
                name_element = card.query_selector('h2 span.a-text-normal') or \
                    card.query_selector('h2 a span') or \
                    card.query_selector('h2 span')
                product_name = self.safe_get_text(name_element)

                # Product URL
                link_element = card.query_selector('h2 a.a-link-normal') or \
                    card.query_selector('a.a-link-normal[href*="/dp/"]')
                href = self.safe_get_attribute(link_element, 'href')
                product_url = f"https://www.amazon.in{href}" if href and href.startswith(
                    '/') else href

                # Image URL
                img_element = card.query_selector('img.s-image')
                image_url = self.safe_get_attribute(img_element, 'src')

                # Discounted price (current price)
                price_element = card.query_selector('.a-price .a-offscreen') or \
                    card.query_selector('span.a-price-whole')
                discounted_price = self.safe_get_text(price_element)

                # Original price (MRP)
                original_element = card.query_selector('.a-price.a-text-price .a-offscreen') or \
                    card.query_selector('span.a-text-price .a-offscreen')
                price = self.safe_get_text(original_element)

                if product_name:
                    products.append({
                        "product_name": product_name,
                        "price": price,
                        "discounted_price": discounted_price,
                        "image_url": image_url,
                        "product_url": product_url
                    })
            except Exception as e:
                continue

        return products
