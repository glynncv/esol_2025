#!/usr/bin/env python3
"""
EUC 2026 Refresh Scope Counter

Counts the number of End User Computing (EUC) devices in scope for 2026 refresh
using configuration from config/esol_criteria.yaml to determine scope criteria.

Requirements:
    pip install pandas openpyxl pyyaml

Usage:
    python euc_2026_count.py [filepath]
    # If no filepath is provided, defaults to data/raw/EUC_ESOL.xlsx
"""

import pandas as pd
import yaml
import sys
import argparse
from pathlib import Path
from typing import Tuple, List, Dict, Any

def load_config(config_path: str = "config/esol_criteria.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        print("Please ensure the config/esol_criteria.yaml file exists.")
        print("You can generate it by running the separated_esol_analyzer.py script first.")
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required configuration sections
        required_sections = ['esol_categories', 'data_mapping']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required configuration section: {section}")
                sys.exit(1)
        
        return config
    except yaml.YAMLError as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)

def validate_columns(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """Validate that required columns exist in the DataFrame."""
    data_mapping = config['data_mapping']
    required_columns = [
        data_mapping['action_column'],
        data_mapping['site_column'],
        data_mapping['cost_column']
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        sys.exit(1)

def load_data(filepath: Path, config: Dict[str, Any], sheet_name: str = 'Export') -> pd.DataFrame:
    """Load and validate Excel data."""
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        validate_columns(df, config)
        
        # Clean and validate cost column using config
        cost_column = config['data_mapping']['cost_column']
        if cost_column in df.columns:
            df[cost_column] = pd.to_numeric(df[cost_column], errors='coerce')
            df[cost_column] = df[cost_column].fillna(0)
        
        return df
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)

def count_devices_in_scope(df: pd.DataFrame, config: Dict[str, Any], target_category: str = 'esol_2026') -> Tuple[pd.DataFrame, int, int, str]:
    """Count devices in scope based on configuration."""
    action_column = config['data_mapping']['action_column']
    
    # Get the action value from config for the target category
    if target_category not in config['esol_categories']:
        print(f"❌ Target category '{target_category}' not found in configuration")
        print(f"Available categories: {list(config['esol_categories'].keys())}")
        sys.exit(1)
    
    action_filter = config['esol_categories'][target_category]['action_value']
    target_date = config['esol_categories'][target_category]['target_date']
    
    mask_2026 = df[action_column] == action_filter
    df_2026 = df[mask_2026]
    count_2026 = len(df_2026)
    total_devices = len(df)
    
    return df_2026, count_2026, total_devices, action_filter

def generate_site_summary(df_2026: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate summary by site with device counts and costs."""
    export_rows = []
    
    if df_2026.empty:
        return export_rows
    
    site_column = config['data_mapping']['site_column']
    cost_column = config['data_mapping']['cost_column']
    
    # Filter out rows with null/empty site names
    df_filtered = df_2026.dropna(subset=[site_column])
    df_filtered = df_filtered[df_filtered[site_column].str.strip() != '']
    
    if df_filtered.empty:
        print("⚠️ No valid site location data found.")
        return export_rows
    
    site_group = df_filtered.groupby(site_column)
    print(f"{'Site':<30} {'Devices':>8} {'Total Cost':>18}")
    print("-" * 60)
    
    for site, group in site_group:
        count = len(group)
        cost = group[cost_column].sum()
        print(f"{site:<30} {count:>8} ${cost:>17,.0f}")
        export_rows.append({'Site': site, '# of Devices': count, 'Replacement Cost': cost})
    
    return export_rows

def export_summary(export_rows: List[Dict[str, Any]], export_path: Path) -> None:
    """Export site summary to CSV file."""
    if not export_rows:
        print("No data to export.")
        return
    
    # Ensure output directory exists
    export_path.parent.mkdir(parents=True, exist_ok=True)
    
    export_df = pd.DataFrame(export_rows)
    export_df = export_df.sort_values(by='Replacement Cost', ascending=False)
    export_df.to_csv(export_path, index=False)
    print(f"\nExported per-site summary to '{export_path}'")

def main():
    parser = argparse.ArgumentParser(
        description='Count EUC devices in scope for ESOL refresh using configuration-driven criteria',
        epilog="""
Examples:
  python euc_2026_count.py                           # Analyze 2026 ESOL devices
  python euc_2026_count.py --category esol_2024     # Analyze 2024 ESOL devices  
  python euc_2026_count.py --category esol_2025     # Analyze 2025 ESOL devices
  python euc_2026_count.py --help-categories        # Show available categories
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('filepath', nargs='?', default='data/raw/EUC_ESOL.xlsx', 
                       help='Path to the Excel file (default: data/raw/EUC_ESOL.xlsx)')
    parser.add_argument('--config-path', default='config/esol_criteria.yaml',
                       help='Path to the ESOL criteria configuration file (default: config/esol_criteria.yaml)')
    parser.add_argument('--category', default='esol_2026',
                       help='ESOL category to analyze (default: esol_2026)')
    parser.add_argument('--sheet-name', default='Export',
                       help='Excel sheet name to read (default: Export)')
    parser.add_argument('--output-path', default='data/processed/euc_2026_site_summary.csv',
                       help='Output CSV path (default: data/processed/euc_2026_site_summary.csv)')
    parser.add_argument('--help-categories', action='store_true',
                       help='Show available ESOL categories and exit')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config_path)
    
    # Show categories if requested
    if args.help_categories:
        print("📋 Available ESOL Categories:")
        print("=" * 50)
        for category, info in config['esol_categories'].items():
            print(f"• {category}")
            print(f"  Description: {info['description']}")
            print(f"  Action Value: '{info['action_value']}'")
            print(f"  Target Date: {info['target_date']}")
            print()
        return
    
    # Get category information from config
    if args.category not in config['esol_categories']:
        print(f"❌ Category '{args.category}' not found in configuration")
        print(f"Available categories: {list(config['esol_categories'].keys())}")
        print("Use --help-categories to see detailed information about each category.")
        sys.exit(1)
    
    category_info = config['esol_categories'][args.category]
    action_filter = category_info['action_value']
    target_date = category_info['target_date']
    description = category_info['description']

    # Load and validate data
    filepath = Path(args.filepath)
    df = load_data(filepath, config, args.sheet_name)

    # Count devices in scope
    df_2026, count_2026, total_devices, actual_action_filter = count_devices_in_scope(df, config, args.category)

    # Print summary
    print(f"\nEUC {args.category.upper()} Refresh Scope Summary for {filepath.name}")
    print(f"----------------------------------------------")
    print(f"Category: {description}")
    print(f"Target Date: {target_date}")
    print(f"Action Filter: '{actual_action_filter}'")
    print(f"Total devices: {total_devices:,}")
    print(f"Devices in scope for {args.category} refresh: {count_2026:,}")
    if total_devices > 0:
        print(f"Percentage in scope: {count_2026 / total_devices * 100:.2f}%")
    else:
        print("No devices found in the file.")

    # Generate and display site summary
    print(f"\nDevices in scope for {args.category} refresh by site:")
    if not df_2026.empty:
        export_rows = generate_site_summary(df_2026, config)
        
        # Export to CSV
        export_path = Path(args.output_path)
        export_summary(export_rows, export_path)
    else:
        print(f"No devices in scope for {args.category} refresh.")

    # Calculate and display total replacement cost
    cost_column = config['data_mapping']['cost_column']
    if not df_2026.empty and cost_column in df_2026.columns:
        total_cost = df_2026[cost_column].sum()
        print(f"\nTotal replacement cost for {args.category} refresh: ${total_cost:,.0f}")
    else:
        print("\nNo cost data available for replacement calculation.")

if __name__ == "__main__":
    main() 