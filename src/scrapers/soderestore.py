import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Optional
from urllib.parse import urljoin
from .base_scraper import BaseScraper
from ..models import Book

class SodereStoreScraper(BaseScraper):
    # This URL seems to be a collection page. The offset determines pagination.
    # The default offset increment seems to be 60 based on the user's url.
    BASE_URL = "https://soderestore.com"
    START_URL = "https://soderestore.com/Books-%E1%88%98%E1%8D%83%E1%88%85%E1%8D%8D%E1%89%B5-c35241255"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return re.sub(r'\s+', ' ', text).strip()

    def scrape(self, limit: int = 100) -> List[Book]:
        books = []
        offset = 0
        items_per_page = 60 # Inferred from the url offset=60
        
        while len(books) < limit:
            print(f"[SodereStore] Scraping offset {offset}...")
            if offset == 0:
                url = self.START_URL
            else:
                url = f"{self.START_URL}?offset={offset}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if response.status_code != 200:
                    print(f"[SodereStore] Failed to fetch offset {offset}: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Based on the grep output, products seem to be in div with class 'grid-product'
                product_items = soup.find_all("div", class_="grid-product")
                
                if not product_items:
                    print(f"[SodereStore] No products found at offset {offset}. Stopping.")
                    break

                for item in product_items:
                    if len(books) >= limit:
                        break

                    # Title and URL
                    # <a href="..." class="grid-product__title" title="...">
                    title_link = item.find("a", class_="grid-product__title")
                    if not title_link:
                        continue
                        
                    raw_title = title_link.get("title")
                    book_url = title_link.get("href")
                    if book_url and not book_url.startswith("http"):
                         book_url = urljoin(self.BASE_URL, book_url)

                    # Extract Author from Title if present (often "Title by Author" or "Title በ Author")
                    # Example: "በይነ-ዲሲፕሊናዊ የሥነ ጽሑፍ ንባብ በ ቴዎድሮስ ገብሬ" -> Title: ... Author: ቴዎድሮስ ገብሬ
                    title = raw_title
                    author = None
                    
                    if raw_title:
                        # Common separators: " by ", " በ "
                        if " በ " in raw_title:
                            parts = raw_title.split(" በ ")
                            title = parts[0].strip()
                            author = parts[-1].strip()
                        elif " by " in raw_title:
                            parts = raw_title.split(" by ")
                            title = parts[0].strip()
                            author = parts[-1].strip()
                        # Sometimes "በ" is at the start (e.g. "By Author - Title"), but usually it's "Title by Author"
                    
                    title = self._clean_text(title)
                    author = self._clean_text(author)

                    # Image
                    # <img ... class="grid-product__picture" src="...">
                    img_tag = item.find("img", class_="grid-product__picture")
                    cover_image = img_tag.get("src") if img_tag else None
                    if cover_image and not cover_image.startswith("http"):
                         cover_image = urljoin(self.BASE_URL, cover_image)

                    book = Book(
                        title=title,
                        author=author,
                        description=None,
                        published_at=None,
                        language="am",
                        cover_image=cover_image,
                        publisher=None,
                        isbn=None,
                        source="SodereStore",
                        url=book_url,
                        category=["Books"]
                    )
                    books.append(book)
                
                # Check if we should continue
                if len(product_items) < items_per_page:
                     # likely the last page
                     break

                offset += items_per_page
                time.sleep(1)

            except Exception as e:
                print(f"[SodereStore] Exception at offset {offset}: {e}")
                break
                
        return books
