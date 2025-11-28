#!/usr/bin/env python3
"""EUC Device Inventory Summary Script - Extracts key metrics for cross-tool validation."""

import pandas as pd
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import add_data_file_argument
from etl.load_data import DataLoader

def main():
    """Extract core EUC metrics and generate standardized summary report."""
    parser = argparse.ArgumentParser(description='EUC device inventory summary for validation')
    add_data_file_argument(parser, 'Path to EUC_ESOL CSV/Excel file')
    parser.add_argument('--output', '-o', help='Output file (optional)')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode for automation')
    args = parser.parse_args()

    # Load configuration and data using centralized loader
    # Find project root (go up from scripts/ to project root)
    project_root = Path(__file__).resolve().parent.parent
    config_path = str(project_root / 'config')
    config_manager = ConfigManager(config_path=config_path)
    loader = DataLoader(config_manager)

    # Load raw data
    try:
        df = loader.load_raw_data(args.data_file)
        # Store the data file path for reporting
        from data_utils import get_data_file_path
        data_file = get_data_file_path(args.data_file)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)

    # Get column names from loader (already cached)
    action_col = loader.action_col
    current_os_col = loader.current_os_col
    edition_col = loader.edition_col

    # Get ESOL action values from loader
    esol_actions = loader.get_esol_category_actions()
    esol_2024_action = esol_actions['esol_2024']
    esol_2025_action = esol_actions['esol_2025']
    esol_2026_action = esol_actions['esol_2026']

    # Extract metrics using centralized loader
    total_devices = len(df)

    # Enterprise and LTSC counts using loader
    enterprise_df = loader.filter_enterprise_devices(df)
    enterprise_count = len(enterprise_df)
    ltsc_count = len(df[df[edition_col] == 'LTSC'])

    # ESOL counts by category using loader
    esol_2024_df = loader.filter_esol_devices(df, categories=['2024'])
    esol_2025_df = loader.filter_esol_devices(df, categories=['2025'])
    esol_2026_df = loader.filter_esol_devices(df, categories=['2026'])
    esol_2024 = len(esol_2024_df)
    esol_2025 = len(esol_2025_df)
    esol_2026 = len(esol_2026_df)
    total_esol = esol_2024 + esol_2025 + esol_2026

    # Windows 11 (Enterprise baseline) using loader
    enterprise_win11_df = loader.filter_win11_devices(enterprise_df, check_installed=True)
    enterprise_win11 = len(enterprise_win11_df)
    win11_adoption = round((enterprise_win11 / enterprise_count) * 100, 1) if enterprise_count > 0 else 0
    enterprise_esol = len(enterprise_df[enterprise_df[action_col].isin([esol_2024_action, esol_2025_action])])
    win11_compatibility = round(((enterprise_win11 + enterprise_esol) / enterprise_count) * 100, 1) if enterprise_count > 0 else 0

    # Kiosk detection using centralized loader
    kiosk_df = loader.filter_kiosk_devices(df)
    total_kiosks = len(kiosk_df)
    enterprise_kiosks = len(kiosk_df[kiosk_df[edition_col] == 'Enterprise'])
    ltsc_kiosks = len(kiosk_df[kiosk_df[edition_col] == 'LTSC'])
    
    # Generate output
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_hash = hashlib.md5(str(total_devices).encode()).hexdigest()[:8]
    
    if args.format == 'json':
        output_str = json.dumps({
            'timestamp': timestamp, 'total_devices': total_devices, 'enterprise_count': enterprise_count,
            'ltsc_count': ltsc_count, 'esol_2024': esol_2024, 'esol_2025': esol_2025, 'esol_2026': esol_2026,
            'win11_adoption': win11_adoption, 'win11_compatibility': win11_compatibility,
            'total_kiosks': total_kiosks, 'enterprise_kiosks': enterprise_kiosks, 'data_hash': data_hash
        }, indent=2)
    else:
        output_str = f"""=== EUC DEVICE INVENTORY SUMMARY ===
Analysis Timestamp: {timestamp}
Data Source: {Path(data_file).name}

DEVICE INVENTORY OVERVIEW:
Total Devices: {total_devices:,}
Enterprise Devices: {enterprise_count:,} ({round((enterprise_count/total_devices)*100, 1)}%)
LTSC Devices: {ltsc_count:,} ({round((ltsc_count/total_devices)*100, 1)}%)

ESOL DEVICE BREAKDOWN:
ESOL 2024 (Urgent): {esol_2024:,} ({round((esol_2024/total_devices)*100, 1)}% of total)
ESOL 2025 (Oct 14): {esol_2025:,} ({round((esol_2025/total_devices)*100, 1)}% of total)
ESOL 2026 (Nov 11): {esol_2026:,} ({round((esol_2026/total_devices)*100, 1)}% of total)
Total Active ESOL: {total_esol:,} ({round((total_esol/total_devices)*100, 1)}% of total)

WINDOWS 11 STATUS (ENTERPRISE BASELINE):
Enterprise Win11 Devices: {enterprise_win11:,}
Win11 Adoption Rate: {win11_adoption}% (Enterprise only)
Win11 Compatibility Rate: {win11_compatibility}% (Enterprise baseline)
Projected Enterprise Win11: {enterprise_win11 + enterprise_esol:,} ({win11_compatibility}% adoption + ESOL replacement)

KIOSK DEVICE ANALYSIS:
Total Kiosk Devices: {total_kiosks:,}
Enterprise Kiosks: {enterprise_kiosks:,} ({round((enterprise_kiosks/total_kiosks)*100, 1) if total_kiosks > 0 else 0}% of total kiosks)
LTSC Kiosks: {ltsc_kiosks:,} ({round((ltsc_kiosks/total_kiosks)*100, 1) if total_kiosks > 0 else 0}% of total kiosks)
Enterprise Kiosks Needing LTSC: {enterprise_kiosks:,}

VALIDATION FINGERPRINT:
Data Hash: {data_hash}
Key Metric Sum: {total_devices + enterprise_count + total_esol + enterprise_win11 + total_kiosks}
Business Rule Version: YAML-2025-v1.0
==================================="""
    
    # Save report
    if args.output:
        Path(args.output).write_text(output_str, encoding='utf-8')
        if not args.quiet: print(f"Summary saved to {args.output}")
    else:
        # Auto-save to data/reports/ with timestamped filename
        output_dir = project_root / 'data' / 'reports'
        output_dir.mkdir(parents=True, exist_ok=True)
        extension = '.json' if args.format == 'json' else '.txt'
        filename = output_dir / f'EUC_Summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}{extension}'
        filename.write_text(output_str, encoding='utf-8')
        if not args.quiet: print(f"Report auto-saved to {filename}")
    
    if not args.quiet: print(output_str)
    return 0

if __name__ == "__main__":
    exit(main())
