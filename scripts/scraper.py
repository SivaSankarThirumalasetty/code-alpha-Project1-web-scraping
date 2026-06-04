"""
scraper.py — Books.toscrape.com scraping module

Reusable class. Separate from notebook so you can import it in other scripts
without re-running the whole analysis.
"""

import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://books.toscrape.com/"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BookScraper:
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "portfolio-scraper/1.0 (educational)"})

    def _get(self, url: str) -> BeautifulSoup | None:
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
                time.sleep(self.delay)
                return BeautifulSoup(resp.text, "html.parser")
            except requests.RequestException as e:
                wait = 2 ** attempt
                logger.warning(f"Attempt {attempt+1} failed for {url}: {e}. Retrying in {wait}s")
                time.sleep(wait)
        logger.error(f"All retries failed for {url}")
        return None

    def get_categories(self) -> dict[str, str]:
        soup = self._get(BASE_URL)
        if not soup:
            return {}
        nav = soup.select("ul.nav-list > li > ul > li > a")
        return {a.text.strip(): urljoin(BASE_URL, a["href"]) for a in nav}

    def scrape_category(self, name: str, url: str) -> list[dict]:
        books = []
        page_url = url
        page_num = 1

        while page_url:
            soup = self._get(page_url)
            if not soup:
                break

            for article in soup.select("article.product_pod"):
                title = article.h3.a["title"]
                price_text = article.select_one(".price_color").text.strip()
                price = float(price_text.replace("£", "").replace("Â", ""))
                rating_word = article.p["class"][1]
                rating = RATING_MAP.get(rating_word, None)

                books.append({
                    "title": title,
                    "category": name,
                    "price_gbp": price,
                    "rating": rating,
                })

            next_btn = soup.select_one("li.next > a")
            if next_btn:
                page_num += 1
                page_url = urljoin(url, next_btn["href"])
                logger.info(f"  {name}: page {page_num}")
            else:
                page_url = None

        return books

    def scrape_all(self, max_categories: int = None) -> list[dict]:
        categories = self.get_categories()
        if max_categories:
            categories = dict(list(categories.items())[:max_categories])

        all_books = []
        for i, (name, url) in enumerate(categories.items(), 1):
            logger.info(f"[{i}/{len(categories)}] Scraping: {name}")
            books = self.scrape_category(name, url)
            all_books.extend(books)
            logger.info(f"  Got {len(books)} books")

        logger.info(f"Total: {len(all_books)} books scraped")
        return all_books


if __name__ == "__main__":
    import pandas as pd
    scraper = BookScraper(delay=1.0)
    data = scraper.scrape_all()
    df = pd.DataFrame(data)
    import os
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/raw_books.csv", index=False)
    print(f"Saved {len(df)} rows")
