import csv
import re
import sys
from abyssinica import romanization
from fidel import Transliterate
from typing import List
from src.models import Book
from src.scrapers.goodreads import GoodreadsScraper
from src.scrapers.ethiobookreview import EthioBookReviewScraper
from src.scrapers.mereb import MerebScraper
from src.scrapers.hahubooks import HahuBooksScraper
from src.scrapers.gebeyaaddis import GebeyaAddisScraper
from src.scrapers.soderestore import SodereStoreScraper


def save_books_to_csv(books: List[Book], filename: str):
    fieldnames = [
        "title",
        "title_en",
        "title_romanized",
        "author",
        "author_romanized",
        "description",
        "published_at",
        "language",
        "cover_image",
        "publisher",
        "isbn",
        "source",
        "url",
        "category",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(
            output_file, fieldnames=fieldnames, extrasaction="ignore"
        )
        dict_writer.writeheader()
        for book in books:
            dict_writer.writerow(book.to_dict())


def main():
    LIMIT_PER_SOURCE = 1
    EXCLUDE_AUTHORS = [
        # r"Abiy\s*Ahmed",
        # r"አብይ\s*አህመድ"
    ]

    exclude_pattern = re.compile("|".join(EXCLUDE_AUTHORS), re.IGNORECASE)

    all_books: List[Book] = []
    seen_titles = set()

    def add_books_if_unique(new_books: List[Book]):
        count = 0
        for book in new_books:
            if not book.title:
                continue

            if EXCLUDE_AUTHORS and book.author and exclude_pattern.search(book.author):
                print(f"Skipping book by excluded author: {book.author} - {book.title}")
                continue

            # Ensure Author is in Amharic if it's currently in English
            if book.author and not re.search(r"[\u1200-\u137F]", book.author):
                try:
                    # If it has no Ethiopic characters, assume it's English/Latin and convert
                    book.author_romanized = (
                        book.author
                    )  # Save original English as romanized
                    # Lowercase is required for fidel to handle capitalization correctly
                    book.author = Transliterate(book.author.lower()).transliterate()
                except Exception as e:
                    print(
                        f"Warning: Failed to transliterate author '{book.author}': {e}"
                    )

            # Romanize if not already present
            if not book.title_romanized and book.title:
                try:
                    book.title_romanized = romanization.romanize(book.title)
                except Exception:
                    book.title_romanized = None

            if not book.author_romanized and book.author:
                try:
                    book.author_romanized = romanization.romanize(book.author)
                except Exception:
                    book.author_romanized = None

            norm_title = " ".join(book.title.strip().lower().split())
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                all_books.append(book)
                count += 1
        return count

    # 1. Scrape Mereb
    try:
        print("\nStarting Mereb Scraper...")
        mereb_scraper = MerebScraper()
        mereb_books = mereb_scraper.scrape(limit=LIMIT_PER_SOURCE)
        added = add_books_if_unique(mereb_books)
        print(
            f"Finished Mereb. Collected {len(mereb_books)} books. Added {added} unique."
        )
    except Exception as e:
        print(f"Mereb Scraper failed: {e}")

    # 2. Scrape EthioBookReview
    try:
        print("\nStarting EthioBookReview Scraper...")
        ebr_scraper = EthioBookReviewScraper()
        ebr_books = ebr_scraper.scrape(limit=LIMIT_PER_SOURCE)
        added = add_books_if_unique(ebr_books)
        print(
            f"Finished EthioBookReview. Collected {len(ebr_books)} books. Added {added} unique."
        )
    except Exception as e:
        print(f"EthioBookReview Scraper failed: {e}")

    # 3. Scrape Goodreads
    try:
        print("\nStarting Goodreads Scraper...")
        gr_scraper = GoodreadsScraper()
        gr_books = gr_scraper.scrape(limit=LIMIT_PER_SOURCE)
        added = add_books_if_unique(gr_books)
        print(
            f"Finished Goodreads. Collected {len(gr_books)} books. Added {added} unique."
        )
    except Exception as e:
        print(f"Goodreads Scraper failed: {e}")

    # 4. Scrape HahuBooks
    try:
        print("\nStarting HahuBooks Scraper...")
        hahu_scraper = HahuBooksScraper()
        hahu_books = hahu_scraper.scrape(limit=LIMIT_PER_SOURCE)
        added = add_books_if_unique(hahu_books)
        print(
            f"Finished HahuBooks. Collected {len(hahu_books)} books. Added {added} unique."
        )
    except Exception as e:
        print(f"HahuBooks Scraper failed: {e}")

    # 5. Scrape GebeyaAddis
    try:
        print("\nStarting GebeyaAddis Scraper...")
        ga_scraper = GebeyaAddisScraper()
        ga_books = ga_scraper.scrape(limit=LIMIT_PER_SOURCE)
        added = add_books_if_unique(ga_books)
        print(
            f"Finished GebeyaAddis. Collected {len(ga_books)} books. Added {added} unique."
        )
    except Exception as e:
        print(f"GebeyaAddis Scraper failed: {e}")

    # 6. Scrape SodereStore
    try:
        print("\nStarting SodereStore Scraper...")
        ss_scraper = SodereStoreScraper()
        ss_books = ss_scraper.scrape(limit=LIMIT_PER_SOURCE)
        added = add_books_if_unique(ss_books)
        print(
            f"Finished SodereStore. Collected {len(ss_books)} books. Added {added} unique."
        )
    except Exception as e:
        print(f"SodereStore Scraper failed: {e}")

    # 7. Save Combined Results
    output_filename = "data/ethiopian_books.csv"
    if all_books:
        save_books_to_csv(all_books, output_filename)
        print(f"\nSUCCESS: Saved total of {len(all_books)} books to {output_filename}")
    else:
        print("\nNo books collected from any source.")


if __name__ == "__main__":
    main()
