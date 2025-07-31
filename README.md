# Dollar Tax Analysis (CGT)

This repository contains the Python code used to analyse the nominal and real gains from buying and selling U.S. dollars after a 12‑month holding period and to estimate the potential revenue from a tiered Capital Gains Tax (CGT) in different market scenarios.

## Overview

The script performs the following steps:

1. **Load data** – imports daily dollar price data and annual inflation rates.
2. **Compute 12‑month returns** – calculates buy and sell prices, nominal gains and real gains (adjusted for inflation).
3. **Visualise trends** – generates line charts of price trends, nominal gains, distributions of real gains and comparisons of average gains by purchase year.
4. **Define a tiered CGT function** – models a stepped tax rate and applies it to individual gains.
5. **Scenario analysis** – evaluates three market scenarios (conservative, median, optimistic) at different realisation rates to estimate total tax revenue, and plots the results.

## Usage

Due to journal restrictions, the dataset is **not included** in this repository. To reproduce the analysis:

1. Obtain the following data files:
   - `dollar_change_columns.csv` – daily dollar prices with columns `open`, `low`, `high`, `close`, `change`, `persent_change`, `miladi_date` and `shamsi_date`.
   - `Iran_Tavarom.xlsx` – annual inflation rates with columns `year_miladi` and `persent`.
2. Create a folder named `data` in the repository root and place the files inside it. The script expects them at `data/dollar_change_columns.csv` and `data/Iran_Tavarom.xlsx`.
3. Install required packages:

   ```bash
   pip install pandas numpy matplotlib seaborn
   ```

4. Run the analysis:

   ```bash
   python tax_analysis.py
   ```

You can comment out or modify sections of the script to generate only the plots or analyses you need.

When the companion paper is published and data restrictions are lifted, the dataset will be added or a link to the source will be provided.

## Repository structure

```
.
├── data/                # Place data files here (not included)
├── tax_analysis.py      # Main analysis script
├── README.md            # Project overview and usage instructions
└── LICENSE              # License for this project (e.g., MIT)
```

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.