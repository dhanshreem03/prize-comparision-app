"""Flipkart Scraper"""
from playwright.sync_api import Page
from .base_scraper import BaseScraper


class FlipkartScraper(BaseScraper):
    """Scraper for Flipkart (flipkart.com)"""

    @property
    def site_name(self) -> str:
        return "Flipkart"

    def get_search_url(self, query: str) -> str:
        return f"https://www.flipkart.com/search?q={query}"

    def wait_for_content(self, page: Page, timeout: int = 15000):
        """Wait for Flipkart product cards to load."""
        # Close login popup if it appears
        try:
            close_btn = page.query_selector('button._2KpZ6l._2doB4z')
            if close_btn:
                close_btn.click()
                page.wait_for_timeout(500)
        except:
            pass

        # Try to close any modal/popup by clicking the X button
        try:
            close_btn = page.query_selector(
                'span._30XB9F') or page.query_selector('button[class*="close"]')
            if close_btn:
                close_btn.click()
                page.wait_for_timeout(500)
        except:
            pass

        # Wait for product containers to load
        try:
            page.wait_for_selector('div[data-id]', timeout=timeout)
        except:
            try:
                page.wait_for_selector('div._1AtVbE', timeout=timeout)
            except:
                try:
                    page.wait_for_selector('a[href*="/p/"]', timeout=timeout)
                except:
                    pass
        page.wait_for_timeout(3000)

    def is_valid_product_name(self, text: str) -> bool:
        """Check if the text is a valid product name."""
        if not text:
            return False

        # Invalid patterns - these are not product names
        invalid_patterns = [
            'currently unavailable',
            'add to compare',
            'add to cart',
            'buy now',
            'view details',
            'out of stock',
            'notify me',
            'coming soon',
            'sold out',
            'see all',
            'view all',
            'sponsored',
            'advertisement',
            '% off',
            'free delivery',
            'bank offer',
            'no cost emi',
            'exchange offer',
        ]

        text_lower = text.lower().strip()

        # Check if text contains any invalid patterns
        for pattern in invalid_patterns:
            if pattern in text_lower:
                return False

        # Valid product names should be between 10-300 chars
        if len(text) < 10 or len(text) > 300:
            return False

        # Should not start with special characters or price symbols
        if text.startswith('₹') or text.startswith('%') or text.startswith('★'):
            return False

        return True

    def parse_products(self, page: Page) -> list[dict]:
        """Parse Flipkart product cards using JS evaluation for reliable extraction."""
        # Use JavaScript to extract all product data at once, avoiding duplicate sub-element issues
        products_data = page.evaluate('''() => {
            const results = [];
            const seen = new Set();
            
            // Find all product card containers
            const cards = document.querySelectorAll('div[data-id], div.slAVV4, div._1sdMkc, div.CGtC98, div._2kHMtA');
            
            cards.forEach(card => {
                try {
                    // Get product link
                    const linkEl = card.querySelector('a[href*="/p/"]');
                    if (!linkEl) return;
                    
                    let href = linkEl.getAttribute('href');
                    if (!href || !href.includes('/p/')) return;
                    
                    const productUrl = href.startsWith('/') ? 'https://www.flipkart.com' + href : href;
                    
                    // Skip duplicates
                    const urlKey = productUrl.split('?')[0];
                    if (seen.has(urlKey)) return;
                    seen.add(urlKey);
                    
                    // Product name - try multiple selectors
                    let productName = null;
                    const nameSelectors = ['div.KzDlHZ', 'div._4rR01T', 'a.s1Q9rs', 'div.syl9yP', 'a.wjcEIp', 'div.IRpwTa', 'a.IRpwTa'];
                    for (const sel of nameSelectors) {
                        const el = card.querySelector(sel);
                        if (el && el.textContent.trim().length >= 10) {
                            productName = el.textContent.trim();
                            break;
                        }
                    }
                    // Fallback: title attribute
                    if (!productName) {
                        productName = linkEl.getAttribute('title') || linkEl.getAttribute('aria-label');
                    }
                    // Fallback: extract from URL slug
                    if (!productName && href) {
                        const urlPart = href.split('/p/')[0];
                        const slug = urlPart.split('/').pop();
                        if (slug && slug.length > 10) {
                            productName = slug.replace(/-/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
                        }
                    }
                    if (!productName || productName.length < 5) return;
                    
                    // Image URL - prefer data-src (lazy load), skip base64
                    let imageUrl = null;
                    const imgEl = card.querySelector('img[src*="rukminim"], img[data-src*="rukminim"], img._396cs4, img.DByuf4, img');
                    if (imgEl) {
                        imageUrl = imgEl.getAttribute('data-src') || imgEl.getAttribute('src');
                        if (imageUrl && imageUrl.startsWith('data:')) imageUrl = null;
                    }
                    
                    // Prices - current/discounted and original/MRP
                    let discountedPrice = null;
                    let originalPrice = null;
                    
                    // Discounted/current price selectors
                    const discountSelectors = ['div.Nx9bqj._4b5DiR', 'div.Nx9bqj', 'div._30jeq3'];
                    for (const sel of discountSelectors) {
                        const el = card.querySelector(sel);
                        if (el) {
                            const txt = el.textContent.trim();
                            if (txt.includes('₹')) {
                                discountedPrice = txt;
                                break;
                            }
                        }
                    }
                    
                    // Original/MRP price selectors (strikethrough) - expanded list
                    const originalSelectors = [
                        'div.yRaY8j.ZYYwLA',   // New strikethrough
                        'div.yRaY8j',           // MRP container
                        'span.yRaY8j',          // Span variant
                        'div._3I9_wc._27UcVY',  // Old strikethrough
                        'div._3I9_wc',          // Old MRP
                        'strike',               // Generic strikethrough
                        's',                    // Another strikethrough tag
                        '[style*="line-through"]', // Inline strikethrough style
                        '.CxhGGd'               // Another MRP class
                    ];
                    for (const sel of originalSelectors) {
                        const el = card.querySelector(sel);
                        if (el) {
                            const txt = el.textContent.trim();
                            if (txt.includes('₹')) {
                                originalPrice = txt.match(/₹[\d,]+/)?.[0] || txt;
                                break;
                            }
                        }
                    }
                    
                    // Additional fallback: look for price in parent container that's different from discounted
                    if (!originalPrice && discountedPrice) {
                        const allPriceEls = card.querySelectorAll('div, span');
                        for (const el of allPriceEls) {
                            const txt = el.textContent.trim();
                            const match = txt.match(/₹[\d,]+/);
                            if (match && match[0] !== discountedPrice && !el.querySelector('div, span')) {
                                // Found a different price that's likely the MRP
                                const val = parseInt(match[0].replace(/[₹,]/g, ''));
                                const discVal = parseInt(discountedPrice.replace(/[₹,]/g, ''));
                                if (val > discVal) {
                                    originalPrice = match[0];
                                    break;
                                }
                            }
                        }
                    }
                    
                    // Fallback: scan for price pattern if nothing found
                    if (!discountedPrice && !originalPrice) {
                        const allText = card.innerText;
                        const priceMatch = allText.match(/₹[\\d,]+/);
                        if (priceMatch) discountedPrice = priceMatch[0];
                    }
                    
                    // price = original MRP (strikethrough), discounted_price = current selling price
                    // If no original price, it means no discount - show discounted as the price
                    const finalPrice = originalPrice || discountedPrice;
                    
                    results.push({
                        product_name: productName,
                        price: finalPrice,
                        discounted_price: discountedPrice,
                        image_url: imageUrl,
                        product_url: productUrl
                    });
                } catch (e) {
                    // skip card on error
                }
            });
            
            return results;
        }''')

        print(
            f"[Flipkart Debug] JS extracted {len(products_data)} unique products")
        return products_data
