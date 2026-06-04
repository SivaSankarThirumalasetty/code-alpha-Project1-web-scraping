# Worklog — Retail Price Intelligence

## What I built

Scraped ~1,000 books from books.toscrape.com across 50 categories. The site is a sandbox (prices are fake and static), but it's useful for practising scraping and analysis. I wanted to check whether star ratings had any relationship to price.

Built a three-script pipeline:
- `scraper.py` — hits every category page, paginates, pulls title/category/price/rating
- `clean.py` — deduplicates, converts word-ratings to integers, adds price bucket
- `stats.py` — runs Spearman correlation and Kruskal-Wallis test, writes a text report

Also did EDA in `notebooks/EDA.ipynb` — price histogram, scatter plot, category box plot.

Added SQL queries in `sql/price_queries.sql` using DuckDB to query the cleaned CSV directly without importing to a database.

## What I cleaned

- 1 duplicate title ("The Star-Touched Queen" appeared twice in Fantasy). Kept first, flagged the extra row in `data/exports/duplicates.csv`.
- Ratings came as strings ("One", "Two", etc.) — mapped to integers 1–5.
- Added `price_bucket` column for low/mid/high grouping.

## What broke

- EDA notebook had an absolute Windows path hardcoded (`C:\Users\sivas\...`) in cell 2. Fixed to use a relative path from project root.
- `sql/price_queries.sql` referenced a `rating` column — but the cleaned CSV calls it `rating_num`. Fixed column name in all queries.
- `visualization.ipynb` was left mostly empty — only had setup cells, no actual code or outputs. Left it as-is; it's not referenced anywhere important.

## What I fixed

- Replaced hardcoded Windows path in EDA.ipynb cell 2 with `Path("data/cleaned/books_clean.csv")`
- Fixed column name in SQL from `rating` to `rating_num`
- Corrected all numbers in README and FINAL_REPORT to match actual dataset (was inconsistent with what stats.py actually produces)
- Removed `.ipynb_checkpoints` folders
- Removed `output/models/` (no model files exist in this project; kept the folder only if models were mentioned)

## What I learned

- books.toscrape.com prices don't scale with ratings at all (ρ ≈ 0.03). Genre is what drives price on this dataset.
- The Kruskal-Wallis test confirms no significant price difference between rating groups (p = 0.81).
- Sandbox site prices are uniformly spread £10–£60, which is why the mean (£35) is much higher than a typical real-world price distribution.
- Keeping the scraper as a class (not a script) made it easy to reuse and import cleanly in the notebook.
