# Ethiopian Book Scraper

Collect data on Ethiopian books from multiple online sources and unify them into a single CSV format compatible with standard database schemas.

## Features

- **Multiple Sources**: Scrapes data from:
  - [Goodreads](https://www.goodreads.com/list/show/89548.Best_Amharic_Books) (Best Amharic Books list)
  - [EthioBookReview](https://www.ethiobookreview.com)
  - [Mereb](https://www.mereb.shop) (Books Category via Algolia API)
  - [HahuBooks](https://www.hahubooks.com)
  - [GebeyaAddis](https://www.gebeyaaddis.com)
  - [SodereStore](https://soderestore.com)
- **Romanization**: Automatically generates Latin-character phonetic versions (transliteration) of Amharic titles and authors using the `abyssinica` library.
- **Amharic Script Normalization**: Automatically detects English/Latin author names and converts them to Amharic script using the `fidel` library to ensure consistency across the dataset.
- **Category Extraction**: Extracts book categories and genres from all sources where available.
- **Unified Data Model**: Standardizes fields across different sources.
- **Deduplication**: Filters out duplicate books based on normalized titles.
- **Filtering**: Ability to exclude books by specific authors.

## Project Structure

```text
.
├── data/                   # Scraped data artifacts (CSV)
├── src/
│   ├── models.py           # Book data model
│   └── scrapers/           # Source-specific scraper implementations
│       ├── base_scraper.py # Abstract base class
│       ├── goodreads.py    # Goodreads implementation
│       ├── mereb.py        # Mereb implementation
│       ├── ethiobookreview.py # EthioBookReview implementation
│       ├── hahubooks.py    # HahuBooks implementation
│       ├── gebeyaaddis.py  # GebeyaAddis implementation
│       └── soderestore.py  # SodereStore implementation
├── main.py                 # Orchestration script
└── .venv/                  # Python virtual environment
```

## Data Schema

The generated CSV (`data/ethiopian_books.csv`) follows this structure:

| Column | Type | Description |
| :--- | :--- | :--- |
| `title` | String | Title of the book (Primary, usually Amharic) |
| `title_en` | String | English title (if available) |
| `title_romanized` | String | Phonetic Latin version of the title |
| `author` | String | Author name (Normalized to Amharic script) |
| `author_romanized` | String | Phonetic Latin version of the author name |
| `description` | Text | Book synopsis (cleaned of newlines) |
| `published_at` | Date | Normalized date (`YYYY-MM-DD`) |
| `language` | String | Language code (default: `am`) |
| `cover_image` | String | URL to the book cover image |
| `publisher` | String | Name of the publisher |
| `isbn` | String | ISBN-13 or ISBN-10 |
| `source` | String | The origin of the data (e.g., Mereb) |
| `url` | String | Source URL for the specific book |
| `category` | String | Pipe-separated list of categories/genres (e.g., `Fiction|Romance`) |

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd book-scraping
   ```

2. **Set up virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install requests beautifulsoup4 abyssinica fidel
   ```

## Usage

To run the full scraping process:

```bash
python3 main.py
```

### Configuration
You can adjust settings directly in `main.py`:

- **Scraping Limits**: Modify `LIMIT_PER_SOURCE` to control how many books to fetch from each site.
- **Author Exclusion**: Add regex patterns to the `EXCLUDE_AUTHORS` list to skip specific authors.

```python
# main.py
LIMIT_PER_SOURCE = 100
EXCLUDE_AUTHORS = [
    r"Author Name",
]
```

## License
MIT
