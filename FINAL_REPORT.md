# FINAL REPORT — Retail Price Intelligence

## Project Objective

Investigate whether star ratings drive book prices on an e-commerce platform (books.toscrape.com). Scraped 1,000 books across 50 categories and applied statistical tests to determine if quality signals (ratings) correlate with pricing.

## Tools Used

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| requests + BeautifulSoup4 | Web scraping |
| pandas | Data cleaning, transformation |
| scipy | Spearman correlation, Kruskal-Wallis test |
| DuckDB | SQL queries on local CSV |
| matplotlib / seaborn | Visualization |
| Jupyter | Exploratory analysis |

## Dataset Source

- **Source:** [books.toscrape.com](http://books.toscrape.com) (sandbox e-commerce site, publicly available)
- **Raw volume:** 1,000 books scraped across 50 categories
- **After cleaning:** 999 books (1 duplicate removed)
- **Features:** Title, category, star rating (1–5), price (GBP), price bucket (low/mid/high)
- **Limitations:** Sandbox site — prices are fixed and synthetic, not real market data. Single scrape, no timestamps.

## Data Cleaning Steps

1. **Loaded raw CSV:** 1,000 rows from `data/raw/raw_books.csv`
2. **Duplicate check:** Found 1 duplicate title ("The Star-Touched Queen", listed twice in Fantasy). Kept first occurrence; wrote flagged row to `data/exports/duplicates.csv`.
3. **Rating conversion:** Ratings scraped as words ("One", "Two", etc.) — mapped to integers 1–5. No unmapped values found.
4. **Price bucketing:** Added `price_bucket` column (low: ≤£20, mid: £20–35, high: >£35) for grouped analysis.
5. **Final shape:** 999 rows × 5 columns (`title`, `category`, `rating_num`, `price_gbp`, `price_bucket`)

## Analysis Steps

1. Descriptive statistics on `price_gbp` (median, mean, std, min, max)
2. Spearman rank correlation between `rating_num` and `price_gbp`
3. Kruskal-Wallis test on price distributions across the five rating groups
4. Per-category median price ranking to identify genre-level price drivers
5. Visualisations: price histogram, rating vs price box+strip plot, category box plot, correlation heatmap, rating distribution, price tier breakdown

## Results

| Metric | Value |
|--------|-------|
| Books analysed | 999 |
| Median price | £36.00 |
| Mean price | £35.07 |
| Std deviation | £14.45 |
| Min / Max price | £10.00 / £59.99 |
| Spearman ρ (rating vs price) | 0.0296 |
| Spearman p-value | 0.3505 |
| Kruskal-Wallis H | 1.5736 |
| Kruskal-Wallis p-value | 0.8135 |

**Key insight:** Rating and price are essentially uncorrelated (ρ = 0.03, p = 0.35). The Kruskal-Wallis test also finds no significant price difference across rating groups (p = 0.81). Genre is the real price driver — Suspense, Novels, and Politics categories have the highest median prices (£47–58); Crime and Academic have the lowest (£11–13).

## Business Insights

1. **Prices are spread fairly evenly from £10 to £60** with no single price cluster. On a real marketplace this would suggest a highly diverse catalogue; here it reflects the synthetic pricing of the sandbox.
2. **Star ratings have no pricing signal** (ρ = 0.03, p = 0.35). Customers cannot use price as a quality proxy on this platform.
3. **Genre is the dominant price driver.** A Suspense book costs nearly 5× a Crime book at the median, regardless of its rating. Category predicts price far better than any quality signal.
4. **Most books (52%) fall in the high price tier** (>£35). Only 20% are in the low tier (<£20).
5. **Rating groups are roughly balanced** (196–226 books each), so the statistical tests are not underpowered by lopsided group sizes.

## Challenges Faced

- Ratings were stored as English words ("One", "Two", …) rather than numbers — required explicit mapping and validation to catch unmapped values.
- One title appeared twice in the same category, requiring a deduplication decision and a separate export for transparency.
- Notebook paths broke when run outside the project root — fixed by using relative `Path()` objects throughout.
- Chose Spearman over Pearson correlation because price is not normally distributed and a linear relationship was not assumed.

## Screenshots

See `screenshots/` folder:

- `charts/price_histogram.png` — price distribution with median/mean lines
- `charts/rating_vs_price_scatter.png` — box + strip plot by rating group
- `charts/category_boxplot.png` — price spread across all 50 categories
- `charts/raw_data_preview.png` — raw dataset preview
- `model_outputs/stats_summary.png` — statistical test output

## Conclusion

On this platform, category (genre) drives price, not perceived quality. A 5-star history book costs more than a 5-star romance novel — but not because of its rating. This finding would need validation on a real marketplace with real pricing signals and a time dimension to be actionable.

**Limitation:** books.toscrape.com is a sandbox site with synthetic prices. These findings cannot be generalised to real retail pricing.

## Future Work

- Apply the same pipeline to a real product feed (e.g. Amazon via a public API) to see if category still dominates when prices are real.
- Add a temporal dimension — scrape the same books on multiple days to track price drift.
- Build an interactive Streamlit dashboard so reviewers can filter by category and explore pricing interactively.
- Add a simple regression model to quantify how much variance in price is explained by category alone vs. category + rating.

---

**Run command:**

```bash
pip install -r requirements.txt
python scripts/scraper.py      # scrape data
python scripts/clean.py        # clean data
python scripts/stats.py        # run statistical tests
jupyter notebook notebooks/EDA.ipynb
jupyter notebook notebooks/visualization.ipynb
```

---

## Author

Siva Sankar — CodeAlpha Data Analytics Internship, Project 1
