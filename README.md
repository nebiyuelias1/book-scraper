# Ethiopian Book Scraper

Collect data on Ethiopian books from multiple online sources and unify them into a single CSV format compatible with standard database schemas.

## Features

- **Multiple Sources**: Scrapes data from:
  - [Goodreads](https://www.goodreads.com/list/show/89548.Best_Amharic_Books) (Best Amharic Books list)
  - [EthioBookReview](https://www.ethiobookreview.com)

## Project Structure

```text
.
├── data/                   # Scraped data artifacts (CSV)
├── src/
│   ├── models.py           # Book data model
│   └── scrapers/           # Source-specific scraper implementations
│       ├── base_scraper.py # Abstract base class
│       ├── goodreads.py    # Goodreads implementation
│       └── ethiobookreview.py # EthioBookReview implementation
├── main.py                 # Orchestration script
└── .venv/                  # Python virtual environment
```

## Data Schema

The generated CSV (`data/ethiopian_books.csv`) follows this structure:

| Column | Type | Description |
| :--- | :--- | :--- |
| `title` | String | Title of the book (Primary) |
| `author` | String | Author name |
| `description` | Text | Book synopsis (cleaned of newlines) |
| `published_at` | Date | Normalized date (`YYYY-MM-DD`) |
| `language` | String | Language code (default: `am`) |
| `cover_image` | String | URL to the book cover image |
| `publisher` | String | Name of the publisher |
| `isbn` | String | ISBN-13 or ISBN-10 |
| `source` | String | The origin of the data (e.g., Goodreads) |
| `url` | String | Source URL for the specific book |

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd book-scraping
   ```

2. **Set up virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install requests beautifulsoup4
   ```

## Usage

To run the full scraping process:

```bash
python3 main.py
```

### Adjusting Limits
You can modify the number of books to scrape from each source in `main.py`:

```python
# main.py
gr_books = gr_scraper.scrape(limit=100) # Change limit here
```

## License
MIT
