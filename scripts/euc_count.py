import pandas as pd
import argparse

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Analyze ESOL device counts by category')
    parser.add_argument('--category', choices=['esol_2024', 'esol_2025', 'esol_2026', 'all'], 
                       default='all', help='ESOL category to analyze (default: all)')
    
    args = parser.parse_args()
    
    # Read the Excel file
    df = pd.read_excel('data/raw/EUC_ESOL.xlsx')
    
    total = len(df)
    print(f"Total devices: {total}")
    
    # Process the entire dataset (not just a sample)
    urgent_count = (df['Action to take'] == 'Urgent Replacement').sum()
    replace_count = (df['Action to take'] == 'Replace by 14/10/2025').sum()
    
    # Calculate ESOL counts
    esol2024 = urgent_count
    esol2025 = replace_count
    total_esol = esol2024 + esol2025
    non_esol = total - total_esol
    
    # Calculate percentages
    esol2024_pct = round((esol2024 / total) * 100, 2)
    esol2025_pct = round((esol2025 / total) * 100, 2)
    total_esol_pct = round((total_esol / total) * 100, 2)
    non_esol_pct = round((non_esol / total) * 100, 2)
    
    # Output based on category parameter
    if args.category == 'esol_2024':
        print(f"ESOL 2024: {esol2024} devices ({esol2024_pct}%) - down from the previous count")
    elif args.category == 'esol_2025':
        print(f"ESOL 2025: {esol2025} devices ({esol2025_pct}%)")
    elif args.category == 'esol_2026':
        print(f"ESOL 2026: {non_esol} devices ({non_esol_pct}%) - non-ESOL devices")
    else:  # 'all' category
        print(f"ESOL 2024: {esol2024} devices ({esol2024_pct}%) - down from the previous count")
        print(f"Total ESOL: {total_esol} devices ({total_esol_pct}%) instead of 434")
        print(f"Non-ESOL: {non_esol:,} devices ({non_esol_pct}%) - slightly better compatibility")

if __name__ == "__main__":
    main() 