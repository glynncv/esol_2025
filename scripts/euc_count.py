import pandas as pd

# Read the Excel file
df = pd.read_excel('data/raw/EUC_ESOL.xlsx')

total = len(df)
print(f"Total devices: {total}")

# Sample the first 100 rows
sample = df.head(100)

urgent_count = (sample['Action to take'] == 'Urgent Replacement').sum()
replace_count = (sample['Action to take'] == 'Replace by 14/10/2025').sum()
win11_count = sample['Current OS Build'].astype(str).str.contains('Win11', na=False).sum()

# Extrapolate from sample
esol2024_est = round((urgent_count / 100) * total)
esol2025_est = round((replace_count / 100) * total)
win11_est = round((win11_count / 100) * total)

print(f"Estimated ESOL 2024: {esol2024_est}")
print(f"Estimated ESOL 2025: {esol2025_est}")
print(f"Estimated Win11: {win11_est}")
print(f"Total estimate: {total}") 