#!/usr/bin/env python3
"""
Helper script to get all available sites from the EUC data file.
Used by generate_all_outputs.bat to discover sites for export.
"""
import pandas as pd
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import get_data_file_path

def main():
    """Get all available sites and print them one per line."""
    try:
        # Load configuration
        project_root = Path(__file__).resolve().parent.parent
        config_path = str(project_root / 'config')
        config_manager = ConfigManager(config_path=config_path)
        esol_config = config_manager.get_esol_criteria()
        
        # Read the Excel file
        data_file = get_data_file_path(None)
        df = pd.read_excel(data_file)
        
        # Get unique sites
        site_col = esol_config['data_mapping']['site_column']
        sites = sorted([s for s in df[site_col].unique() if pd.notna(s)])
        
        # Print each site on a separate line
        for site in sites:
            print(site)
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())









