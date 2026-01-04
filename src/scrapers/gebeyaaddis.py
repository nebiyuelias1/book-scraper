import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Optional
from .base_scraper import BaseScraper
from ..models import Book

class GebeyaAddisScraper(BaseScraper):
    BASE_URL = "https://www.gebeyaaddis.com"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return re.sub(r'\s+', ' ', text).strip()

    def _get_author_from_detail(self, url: str) -> Optional[str]:
        try:
            # Short timeout for detail page to avoid slowing down too much
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract from OG description
            # <meta property="og:description" content="በ እስከዳር አስማረ" />
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                content = og_desc["content"]
                # Remove "በ" (By) if present
                if "በ" in content:
                    parts = content.split("በ")
                    if len(parts) > 1:
                        return self._clean_text(parts[-1])
                return self._clean_text(content)
            
            return None
        except Exception as e:
            print(f"[GebeyaAddis] Error fetching detail {url}: {e}")
            return None

    def scrape(self, limit: int = 100) -> List[Book]:
        books = []
        page = 1
        
        while len(books) < limit:
            print(f"[GebeyaAddis] Scraping page {page}...")
            # Using the book category pagination
            url = f"{self.BASE_URL}/product-category/books/page/{page}/"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if response.status_code != 200:
                    # If 404, we likely reached the end of pages
                    if response.status_code == 404:
                         print(f"[GebeyaAddis] Page {page} not found. Stopping.")
                    else:
                         print(f"[GebeyaAddis] Failed to fetch page {page}: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.content, "html.parser")
                product_items = soup.find_all("li", class_="product")
                
                if not product_items:
                    print(f"[GebeyaAddis] No products found on page {page}. Stopping.")
                    break

                for item in product_items:
                    if len(books) >= limit:
                        break

                    # Title and URL
                    title_tag = item.find("h2", class_="woocommerce-loop-product__title")
                    link_tag = item.find("a", class_="woocommerce-LoopProduct-link")
                    
                    if not title_tag or not link_tag:
                        continue

                    title = self._clean_text(title_tag.text)
                    book_url = link_tag.get("href")
                    
                    # Image
                    img_tag = item.find("img")
                    cover_image = img_tag.get("src") if img_tag else None

                    # Author (Fetch from detail page)
                    author = None
                    if book_url:
                        # We only fetch detail if we have a URL. 
                        # To be polite and fast, we might skip this if we want speed, 
                        # but the requirement implies extracting details.
                        # I'll add a small sleep to be polite.
                        author = self._get_author_from_detail(book_url)
                        time.sleep(0.5) 

                    book = Book(
                        title=title,
                        author=author,
                        description=None,
                        published_at=None,
                        language="am",
                        cover_image=cover_image,
                        publisher=None,
                        isbn=None,
                        source="GebeyaAddis",
                        url=book_url
                    )
                    books.append(book)
                
                page += 1
                time.sleep(1) # Sleep between list pages

            except Exception as e:
                print(f"[GebeyaAddis] Exception on page {page}: {e}")
                break
                
        return books
