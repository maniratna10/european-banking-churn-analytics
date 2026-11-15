# European Banking Customer Segmentation & Churn Analytics

## Project overview
This project analyses 10,000 customer records from the supplied European Bank CSV. It examines churn across geography, age, credit-score bands, tenure, account balances, gender, activity and product holding.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install packages:
   `pip install -r requirements.txt`
5. Start the dashboard:
   `streamlit run app.py`

The dashboard opens in your browser. Keep `data/european_bank.csv` in its existing location relative to `app.py`.

## Project contents
- `app.py` — Streamlit dashboard
- `data/european_bank.csv` — supplied dataset copy
- `src/analysis.py` — reproducible validation and segmentation checks
- `reports/research_paper.docx` — EDA, findings and recommendations
- `reports/executive_summary.docx` — short stakeholder summary
- `reports/analysis_notes.md` — assumptions and interpretation notes

## Analytical definitions
- Age bands: Under 30, 30–45, 46–59, and 60+. The supplied brief's 46–60 and 60+ ranges overlap at age 60, so age 60 is assigned to 60+ to keep groups mutually exclusive.
- Tenure: new 0–3 years, mid-term 4–7 years, long-term 8–10 years.
- Credit score: low, medium and high based on dataset tertiles (approximately equal-sized groups).
- Balance: zero balance; low balance below the median of positive balances; high balance at or above that median.
- High-value balance: balance at or above the 75th percentile of positive balances. This is an analytical proxy only, not a bank profitability classification.

## Important interpretation
`Balance` is an account balance, not revenue. The sum of balances belonging to exited customers is described as balance exposure, not lost revenue. The dataset does not contain product margin, customer lifetime value, transaction activity, or actual revenue. Churn patterns are descriptive associations and do not establish causation.

## Data notes
The CSV contains an additional `Year` field (all records are 2025), beyond the columns listed in the project brief. It is retained in the source data but not used as a segmentation dimension. `Surname` is excluded from dashboard analysis. No duplicate rows, duplicate customer IDs or missing values were detected in the supplied file.

## Deployment
For Streamlit Community Cloud, push this folder to a GitHub repository, select `app.py` as the main file, and deploy. Ensure `requirements.txt` and the `data` folder are committed. Do not publish identifiable customer-level data publicly unless you have permission; use an anonymised dataset for a public deployment.
