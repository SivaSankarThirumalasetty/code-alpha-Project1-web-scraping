-- price_queries.sql
-- Run via DuckDB: duckdb -c "SELECT ... FROM read_csv_auto('data/cleaned/books_clean.csv')"
-- Or use the notebook which wraps these with duckdb.connect()
-- Note: column name is rating_num (integer 1-5), not rating

-- ─── 1. Category summary ────────────────────────────────────────────────────
-- Median price and avg rating per category, sorted by median price descending
SELECT
    category,
    COUNT(*)                                        AS book_count,
    ROUND(MEDIAN(price_gbp), 2)                     AS median_price,
    ROUND(AVG(price_gbp), 2)                        AS mean_price,
    ROUND(AVG(rating_num), 2)                       AS avg_rating
FROM books
GROUP BY category
ORDER BY median_price DESC;


-- ─── 2. Price percentiles by category ───────────────────────────────────────
SELECT
    category,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price_gbp), 2) AS p25,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY price_gbp), 2) AS median,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price_gbp), 2) AS p75,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY price_gbp), 2) AS p90
FROM books
GROUP BY category
ORDER BY median DESC;


-- ─── 3. Rating vs price rank divergence ─────────────────────────────────────
-- Books where price rank and rating rank differ the most
-- High divergence = "overpriced" (high price, low rating) or "underpriced" (low price, high rating)
WITH ranked AS (
    SELECT
        title,
        category,
        price_gbp,
        rating_num,
        RANK() OVER (ORDER BY price_gbp DESC)      AS price_rank,
        RANK() OVER (ORDER BY rating_num DESC)     AS rating_rank
    FROM books
)
SELECT
    title,
    category,
    price_gbp,
    rating_num,
    price_rank,
    rating_rank,
    ABS(price_rank - rating_rank) AS rank_divergence
FROM ranked
ORDER BY rank_divergence DESC
LIMIT 20;


-- ─── 4. Distribution of prices by rating bucket ─────────────────────────────
SELECT
    rating_num,
    COUNT(*)                                        AS count,
    ROUND(MEDIAN(price_gbp), 2)                     AS median_price,
    ROUND(MIN(price_gbp), 2)                        AS min_price,
    ROUND(MAX(price_gbp), 2)                        AS max_price
FROM books
WHERE rating_num IS NOT NULL
GROUP BY rating_num
ORDER BY rating_num;


-- ─── 5. Top 10 categories by book count ─────────────────────────────────────
SELECT
    category,
    COUNT(*) AS book_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_catalog
FROM books
GROUP BY category
ORDER BY book_count DESC
LIMIT 10;
