"""
stats.py — Statistical analysis for Retail Price Intelligence.

Runs Spearman correlation and Kruskal-Wallis test on cleaned book data.
Outputs results to output/reports/stats_summary.txt
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from scipy import stats
from pathlib import Path

CLEAN_PATH = Path("data/cleaned/books_clean.csv")
REPORT_PATH = Path("output/reports/stats_summary.txt")
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def run_analysis():
    df = pd.read_csv(CLEAN_PATH)

    # Spearman correlation: rating vs price
    rho, p_spearman = stats.spearmanr(df["rating_num"], df["price_gbp"])

    # Kruskal-Wallis: price distributions across rating groups
    groups = [group["price_gbp"].values for _, group in df.groupby("rating_num")]
    h_stat, p_kruskal = stats.kruskal(*groups)

    report = f"""
=== Retail Price Intelligence — Statistical Summary ===

Dataset: {len(df):,} books (after dedup + zero-price drops)

Spearman Correlation (rating vs price)
  rho = {rho:.4f}
  p = {p_spearman:.4f}
  Interpretation: {'No significant correlation' if p_spearman > 0.05 else 'Significant correlation'}

Kruskal-Wallis Test (price distributions by rating group)
  H = {h_stat:.4f}
  p = {p_kruskal:.4f}
  Interpretation: {'No significant difference between groups' if p_kruskal > 0.05 else 'Significant difference'}

Price summary:
  Median: £{df['price_gbp'].median():.2f}
  Mean:   £{df['price_gbp'].mean():.2f}
  Std:    £{df['price_gbp'].std():.2f}
  Min:    £{df['price_gbp'].min():.2f}
  Max:    £{df['price_gbp'].max():.2f}
"""
    print(report)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"Report saved -> {REPORT_PATH}")
    print("Process completed successfully.")


if __name__ == "__main__":
    run_analysis()
