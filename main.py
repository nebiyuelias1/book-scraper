import csv
import sys
from typing import List
from src.models import Book
from src.scrapers.goodreads import GoodreadsScraper
from src.scrapers.ethiobookreview import EthioBookReviewScraper

def save_books_to_csv(books: List[Book], filename: str):
    fieldnames = ["title", "author", "description", "published_at", "language", "cover_image", "publisher", "isbn", "source", "url"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames, extrasaction='ignore')
        dict_writer.writeheader()
        for book in books:
            dict_writer.writerow(book.to_dict())

def main():
    all_books: List[Book] = []
    seen_titles = set()

    def add_books_if_unique(new_books: List[Book]):
        count = 0
        for book in new_books:
            if not book.title:
                continue
            # Normalize title for comparison
            norm_title = " ".join(book.title.strip().lower().split())
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                all_books.append(book)
                count += 1
        return count

    # 1. Scrape Goodreads
    try:
        print("Starting Goodreads Scraper...")
        gr_scraper = GoodreadsScraper()
        # You can adjust the limit here
        gr_books = gr_scraper.scrape(limit=10) 
        added = add_books_if_unique(gr_books)
        print(f"Finished Goodreads. Collected {len(gr_books)} books. Added {added} unique.")
    except Exception as e:
        print(f"Goodreads Scraper failed: {e}")

    # 2. Scrape EthioBookReview
    try:
        print("\nStarting EthioBookReview Scraper...")
        ebr_scraper = EthioBookReviewScraper()
        # You can adjust the limit here
        ebr_books = ebr_scraper.scrape(limit=10)
        added = add_books_if_unique(ebr_books)
        print(f"Finished EthioBookReview. Collected {len(ebr_books)} books. Added {added} unique.")
    except Exception as e:
        print(f"EthioBookReview Scraper failed: {e}")

    # 3. Save Combined Results
    output_filename = 'data/ethiopian_books.csv'
    if all_books:
        save_books_to_csv(all_books, output_filename)
        print(f"\nSUCCESS: Saved total of {len(all_books)} books to {output_filename}")
    else:
        print("\nNo books collected from any source.")

if __name__ == "__main__":
    main()
