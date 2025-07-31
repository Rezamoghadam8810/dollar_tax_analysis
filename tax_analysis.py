#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analysis of dollar price gains and simulation of tiered capital‑gains tax (CGT).

This script loads historical dollar price data and inflation rates, calculates
12‑month nominal and real gains for holding periods, produces various
visualisations, and estimates government revenue from a tiered CGT under
different market scenarios.

To reproduce the analysis, place the data files in a ``data`` folder at the
repository root and adjust ``DATA_DIR`` if necessary. The expected files are:

* ``dollar_change_columns.csv`` – daily dollar prices with columns ``open``,
  ``low``, ``high``, ``close``, ``change``, ``persent_change``,
  ``miladi_date`` and ``shamsi_date``.
* ``Iran_Tavarom.xlsx`` – annual inflation rates with columns
  ``year_miladi`` and ``persent``.

Note: Data files are not included in this repository due to publication
restrictions. When the companion paper is published, the data will be
added or a link to the source will be provided.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from pathlib import Path

# Configure plotting aesthetics
sns.set(font_scale=1.1)

# ---------------------------------------------------------------------------
# 1. Data loading and preparation
# ---------------------------------------------------------------------------
# Directory where data files are stored
DATA_DIR = Path(__file__).resolve().parent / "data"

# Load dollar price data
df_dollar = pd.read_csv(DATA_DIR / "dollar_change_columns.csv")

# Load inflation data
df_inflation = pd.read_excel(DATA_DIR / "Iran_Tavarom.xlsx")

# Rename columns for consistency
df_dollar = df_dollar.rename(
    columns={
        "open": "Open",
        "low": "Low",
        "high": "High",
        "close": "Close",
        "change": "Change",
        "persent_change": "ChangePercent",
        "miladi_date": "MiladiDate",
        "shamsi_date": "ShamsiDate",
    }
)

# Parse dates and set index
df_dollar["MiladiDate"] = pd.to_datetime(df_dollar["MiladiDate"], errors="coerce")
df_dollar = df_dollar.set_index("MiladiDate").sort_index()

# Convert numeric columns and handle missing values
for col in ["Open", "Low", "High", "Close", "Change"]:
    df_dollar[col] = (
        df_dollar[col]
        .replace("-", np.nan)
        .astype(str)
        .str.replace(",", "")
        .astype(float)
    )

# ---------------------------------------------------------------------------
# 2. Extract 12‑month buy and sell prices
# ---------------------------------------------------------------------------
monthly = df_dollar.copy()
monthly["BuyPrice"] = monthly["Close"].resample("M").last()
monthly["BuyDate"] = monthly.index
monthly["SellDate"] = monthly["BuyDate"] + pd.DateOffset(months=12)
monthly = monthly.dropna(subset=["BuyPrice", "SellDate"])

# Prepare sell prices (nearest date to SellDate)
df_prices = df_dollar[["Close"]].rename(columns={"Close": "SellPrice"})
df_prices["Date"] = df_prices.index

monthly = pd.merge_asof(
    monthly.sort_values("SellDate"),
    df_prices.sort_values("Date"),
    left_on="SellDate",
    right_on="Date",
    direction="nearest",
)

monthly["SellPriceDate"] = monthly["Date"]
monthly = monthly.drop(columns=["Date"])

# ---------------------------------------------------------------------------
# 3. Nominal and real gain calculations
# ---------------------------------------------------------------------------
monthly["GainNominal"] = monthly["SellPrice"] - monthly["BuyPrice"]
monthly["BuyYear"] = monthly["BuyDate"].dt.year

df_inflation = df_inflation.rename(
    columns={"year_miladi": "BuyYear", "persent": "InflationRate"}
)
df_all = pd.merge(monthly, df_inflation, on="BuyYear", how="left")
df_all["GainReal"] = df_all["GainNominal"] / (1 + df_all["InflationRate"] / 100)
df_final = df_all.copy()

# ---------------------------------------------------------------------------
# 4. Basic analysis plots
# ---------------------------------------------------------------------------
def plot_price_trend():
    plt.figure(figsize=(12, 5))
    plt.plot(df_dollar.index, df_dollar["Close"], color="royalblue")
    plt.title("روند قیمت بسته‌ شدن دلار")
    plt.xlabel("تاریخ")
    plt.ylabel("قیمت (ریال)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.show()


def plot_nominal_gain():
    plt.figure(figsize=(12, 5))
    sns.lineplot(
        data=df_final,
        x="SellDate",
        y="GainNominal",
        marker="o",
        color="darkorange",
    )
    plt.title("سود اسمی نگهداری دلار به مدت ۱۲ ماه")
    plt.xlabel("تاریخ فروش")
    plt.ylabel("سود اسمی (ریال)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_real_gain_distribution():
    plt.figure(figsize=(12, 5))
    ax = sns.histplot(df_final["GainReal"], bins=30, kde=True, color="seagreen")
    for patch in ax.patches:
        height = patch.get_height()
        if height > 0:
            ax.text(
                patch.get_x() + patch.get_width() / 2,
                height + 1,
                f"{int(height)}",
                ha="center",
                fontsize=8,
            )
    plt.title("توزیع سود واقعی معاملات دلار پس از ۱۲ ماه")
    plt.xlabel("سود واقعی (ریال)")
    plt.ylabel("تعداد معاملات")
    plt.tight_layout()
    plt.show()


def plot_buy_sell_comparison():
    fig, ax = plt.subplots(figsize=(14, 5))
    sns.lineplot(
        data=df_final,
        x="BuyDate",
        y="BuyPrice",
        label="قیمت خرید",
        color="orange",
        ax=ax,
    )
    sns.lineplot(
        data=df_final,
        x="BuyDate",
        y="SellPrice",
        label="قیمت فروش (۱۲ ماه بعد)",
        color="green",
        ax=ax,
    )
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.title("مقایسه قیمت خرید و فروش دلار در بازه ۱۲ ماهه")
    plt.xlabel("تاریخ خرید")
    plt.ylabel("قیمت (ریال)")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_gain_by_year():
    df_grouped = df_final.groupby("BuyYear")[["GainNominal", "GainReal"]].mean().reset_index()
    plt.figure(figsize=(12, 5))
    plt.plot(df_grouped["BuyYear"], df_grouped["GainNominal"], marker="o", label="سود اسمی")
    plt.plot(
        df_grouped["BuyYear"],
        df_grouped["GainReal"],
        marker="s",
        linestyle="--",
        label="سود واقعی",
    )
    plt.title("مقایسه میانگین سود اسمی و واقعی به تفکیک سال خرید")
    plt.xlabel("سال خرید")
    plt.ylabel("مقدار سود (ریال)")
    plt.legend()
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 5. Define tiered CGT function
# ---------------------------------------------------------------------------
def calculate_cgt_plakani(amount: float) -> float:
    """Calculate tiered capital‑gains tax based on a stepped rate structure."""
    if amount <= 50_000_000:
        return amount * 0.15
    elif amount <= 100_000_000:
        return (50_000_000 * 0.15) + ((amount - 50_000_000) * 0.20)
    else:
        return (
            (50_000_000 * 0.15)
            + (50_000_000 * 0.20)
            + ((amount - 100_000_000) * 0.25)
        )


# ---------------------------------------------------------------------------
# 6. Scenario simulation and sensitivity analysis
# ---------------------------------------------------------------------------
def run_scenarios():
    scenarios = {
        "محافظه‌کارانه": {"people": 850_000, "volume": 2_000},
        "میانه": {"people": 4_250_000, "volume": 5_000},
        "خوش‌بینانه": {"people": 8_500_000, "volume": 10_000},
    }
    realization_rates = [0.5, 0.7, 0.9]
    yearly_dollar_rate = {2020: 20000, 2021: 25000, 2022: 30000, 2023: 40000, 2024: 50000}
    gain_real_avg_by_year = df_final.groupby("BuyYear")["GainReal"].mean().to_dict()

    results = []
    for year in range(2020, 2025):
        for scenario_name, scenario in scenarios.items():
            for rate in realization_rates:
                gain_real = gain_real_avg_by_year.get(year, np.nan)
                if np.isnan(gain_real):
                    continue
                dollar_value = yearly_dollar_rate[year]
                dollar_volume = scenario["volume"]
                people = scenario["people"]

                gain_person = gain_real / dollar_value * dollar_volume
                tax_person = calculate_cgt_plakani(gain_person)
                total_tax = tax_person * people * rate

                results.append(
                    {
                        "سال": year,
                        "سناریو": scenario_name,
                        "نرخ تحقق": f"{int(rate * 100)}%",
                        "تعداد افراد": people,
                        "حجم دلاری فرد": dollar_volume,
                        "سود واقعی هر نفر (ریال)": round(gain_person),
                        "مالیات هر نفر (ریال)": round(tax_person),
                        "کل مالیات دولت (ریال)": round(total_tax),
                    }
                )
    return pd.DataFrame(results)


def plot_cgt_summary(df_summary: pd.DataFrame) -> None:
    plt.figure(figsize=(14, 6))
    sns.barplot(
        data=df_summary,
        x="سال",
        y="کل مالیات دولت (ریال)",
        hue="سناریو",
        ci=None,
    )
    plt.title("درآمد CGT دولت از معاملات دلار در سناریوهای مختلف")
    plt.xlabel("سال")
    plt.ylabel("کل درآمد مالیاتی (ریال)")
    plt.legend(title="سناریو")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Generate basic plots
    plot_price_trend()
    plot_nominal_gain()
    plot_real_gain_distribution()
    plot_buy_sell_comparison()
    plot_gain_by_year()

    # Run scenario analysis and plot summary
    summary_df = run_scenarios()
    plot_cgt_summary(summary_df)