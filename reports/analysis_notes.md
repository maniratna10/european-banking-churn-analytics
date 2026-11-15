# Analysis notes and definitions

- Dataset size: 10,000 rows × 14 columns.
- Dataset year field: [2025].
- Missing values: 0.
- Duplicate rows: 0.
- Duplicate CustomerId values: 0.
- Overall churn: 2,037 / 10,000 = 20.37%.
- Highest country churn rate: Germany (32.44%; 814 churners from 2,509 customers).
- Age band with highest churn: 46–59 (51.10%; n=1,585).
- Inactive-member churn: 26.85%; active-member churn: 14.27%.
- Female churn: 25.07%; male churn: 16.46%.
- High-value balance threshold: €139,512.29, the 75th percentile among customers with positive balances.
- High-value balance group: 1,596 customers, 367 churners, churn rate 22.99%.
- Total balance held by churned customers: €185,588,094.63. This is balance exposure only, not revenue loss.
- Median of positive balances: €119,839.69; used to distinguish low and high positive balances.
- Credit score bands use qcut tertiles, not externally prescribed credit-risk thresholds.
- Age 60 belongs to the 60+ band to avoid overlap between the brief's suggested 46–60 and 60+ ranges.
