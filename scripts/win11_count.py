import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime

def main():
    """Analyze Windows 11 EUC counts and export summary report."""
    parser = argparse.ArgumentParser(description='Analyze Windows 11 EUC counts')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    args = parser.parse_args()
    
    # Read the Excel file
    df = pd.read_excel('data/raw/EUC_ESOL.xlsx')
    
    # Filter for Windows 11 EUCs - Column "OS Build" begins with "Win11"
    win11_mask = df['OS Build'].str.startswith('Win11', na=False)
    total_eucs = len(df)
    total_win11 = len(df[win11_mask])
    win11_pct = round((total_win11 / total_eucs) * 100, 2) if total_eucs > 0 else 0
    
    # Generate report content
    report_content = f"""# Windows 11 EUC Count Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Total # of EUCs:** {total_eucs:,}
**Total # (%) of Win 11 EUCs:** {total_win11:,} ({win11_pct}%)"""
    
    # Print to console
    print(f"Total # of EUCs: {total_eucs:,}")
    print(f"Total # (%) of Win 11 EUCs: {total_win11:,} ({win11_pct}%)")
    
    # Save report
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report_content, encoding='utf-8')
        print(f"📄 Report saved to {args.output}")
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('data/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f'Win11_Count_{timestamp}.md'
        filename.write_text(report_content, encoding='utf-8')
        print(f"📄 Report auto-saved to {filename}")

if __name__ == "__main__":
    main()