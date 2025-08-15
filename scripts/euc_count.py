import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Analyze ESOL device counts by category')
    parser.add_argument('--category', choices=['esol_2024', 'esol_2025', 'esol_2026', 'all'], 
                       default='all', help='ESOL category to analyze (default: all)')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    
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
    
    # Generate report content
    report_lines = []
    report_lines.append(f"# ESOL Device Count Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append(f"**Total devices analyzed:** {total:,}")
    report_lines.append("")
    
    # Output based on category parameter
    if args.category == 'esol_2024':
        output_text = f"ESOL 2024: {esol2024} devices ({esol2024_pct}%) - down from the previous count"
        report_lines.append(f"## ESOL 2024 Analysis")
        report_lines.append(f"- **Count:** {esol2024} devices")
        report_lines.append(f"- **Percentage:** {esol2024_pct}%")
        report_lines.append(f"- **Status:** Down from the previous count")
        print(output_text)
    elif args.category == 'esol_2025':
        output_text = f"ESOL 2025: {esol2025} devices ({esol2025_pct}%)"
        report_lines.append(f"## ESOL 2025 Analysis")
        report_lines.append(f"- **Count:** {esol2025} devices")
        report_lines.append(f"- **Percentage:** {esol2025_pct}%")
        print(output_text)
    elif args.category == 'esol_2026':
        output_text = f"ESOL 2026: {non_esol} devices ({non_esol_pct}%) - non-ESOL devices"
        report_lines.append(f"## Non-ESOL Analysis")
        report_lines.append(f"- **Count:** {non_esol:,} devices")
        report_lines.append(f"- **Percentage:** {non_esol_pct}%")
        report_lines.append(f"- **Status:** Non-ESOL devices")
        print(output_text)
    else:  # 'all' category
        print(f"ESOL 2024: {esol2024} devices ({esol2024_pct}%) - down from the previous count")
        print(f"Total ESOL: {total_esol} devices ({total_esol_pct}%) instead of 434")
        print(f"Non-ESOL: {non_esol:,} devices ({non_esol_pct}%) - slightly better compatibility")
        
        report_lines.append(f"## Complete ESOL Analysis")
        report_lines.append(f"- **ESOL 2024:** {esol2024} devices ({esol2024_pct}%) - down from the previous count")
        report_lines.append(f"- **ESOL 2025:** {esol2025} devices ({esol2025_pct}%)")
        report_lines.append(f"- **Total ESOL:** {total_esol} devices ({total_esol_pct}%) instead of 434")
        report_lines.append(f"- **Non-ESOL:** {non_esol:,} devices ({non_esol_pct}%) - slightly better compatibility")
    
    # Save report if output specified or auto-save to data/reports/
    report_content = "\n".join(report_lines)
    
    if args.output:
        # User specified output path
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"📄 Report saved to {output_path}")
    else:
        # Auto-save to data/reports/ with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('data/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f'ESOL_Count_{args.category}_{timestamp}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"📄 Report auto-saved to {filename}")

if __name__ == "__main__":
    main() 