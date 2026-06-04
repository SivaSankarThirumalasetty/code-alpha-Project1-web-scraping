"""
clean.py — Data cleaning for Retail Price Intelligence project.

Reads raw_books.csv, applies documented cleaning decisions, writes:
  - books_clean.csv  (main analysis file)
  - duplicates.csv   (flagged duplicate titles)
"""

import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/raw_books.csv")
CLEAN_PATH = Path("data/cleaned/books_clean.csv")
DUPS_PATH = Path("data/exports/duplicates.csv")

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}
PRICE_BINS = [0, 20, 35, float("inf")]
PRICE_LABELS = ["low", "mid", "high"]


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} rows from {path}")
    return df


def drop_zero_price(df: pd.DataFrame) -> pd.DataFrame:
    """Drop 3 books priced at £0 — data artifact on sandbox site, not real listings."""
    mask = df["price_gbp"] > 0
    dropped = (~mask).sum()
    if dropped:
        print(f"Dropped {dropped} zero-price rows (data artifact)")
    return df[mask].copy()


def convert_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Convert word ratings ('One'..'Five') to integers 1..5."""
    if "rating_word" in df.columns:
        df["rating_num"] = df["rating_word"].map(RATING_MAP)
    elif "rating" in df.columns:
        df["rating_num"] = df["rating"]
    else:
        raise KeyError("Neither 'rating_word' nor 'rating' found in data")
        
    unmapped = df["rating_num"].isna().sum()
    if unmapped:
        raise ValueError(f"{unmapped} rows had unmapped rating words — check source")
    return df


def flag_and_dedup(df: pd.DataFrame):
    """
    Some titles appear in multiple genre pages (~4% of records).
    Keep first occurrence; write duplicates to a separate file for reference.
    """
    dups_mask = df.duplicated(subset=["title"], keep="first")
    dups_df = df[dups_mask][["title", "category", "price_gbp"]].copy()
    dups_df.columns = ["title", "category_duplicate", "price_gbp"]

    # Merge category of first occurrence for context
    first = df.drop_duplicates(subset=["title"], keep="first")[["title", "category"]]
    first.columns = ["title", "category_first_seen"]
    dups_df = dups_df.merge(first, on="title")[
        ["title", "category_first_seen", "category_duplicate", "price_gbp"]
    ]

    clean_df = df[~dups_mask].copy()
    print(f"Flagged {len(dups_df)} duplicates; keeping {len(clean_df)} unique titles")
    return clean_df, dups_df


def add_price_bucket(df: pd.DataFrame) -> pd.DataFrame:
    df["price_bucket"] = pd.cut(
        df["price_gbp"], bins=PRICE_BINS, labels=PRICE_LABELS, right=True
    )
    return df


def main():
    df = load_raw(RAW_PATH)
    df = drop_zero_price(df)
    df = convert_ratings(df)
    df, dups_df = flag_and_dedup(df)
    df = add_price_bucket(df)

    keep_cols = ["title", "category", "rating_num", "price_gbp", "price_bucket"]
    df[keep_cols].to_csv(CLEAN_PATH, index=False)
    dups_df.to_csv(DUPS_PATH, index=False)

    print(f"Saved cleaned data -> {CLEAN_PATH}")
    print(f"Saved duplicates   -> {DUPS_PATH}")
    print(f"\nFinal shape: {df.shape}")
    print(f"Median price: £{df['price_gbp'].median():.2f}")
    print(f"Spearman rho (approx sample): check notebooks/EDA.ipynb for full stat")


if __name__ == "__main__":
    main()
