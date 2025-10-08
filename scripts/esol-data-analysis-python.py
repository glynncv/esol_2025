#!/usr/bin/env python3
"""
ESOL Data Analysis Tool
Analyzes EUC device data to track Technical Debt Remediation OKR progress

Requirements:
    pip install pandas openpyxl

Usage:
    python esol_analysis.py [filepath]
"""

import pandas as pd
import sys
from pathlib import Path
from typing import Dict, Tuple, List
import argparse
from datetime import datetime
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

class ESOLAnalyzer:
    """Analyzes ESOL (End of Service Life) device data for OKR tracking"""
    
    def __init__(self, filepath: str):
        """Initialize with Excel file path"""
        self.filepath = Path(filepath)
        self.data = None
        self.total_devices = 0
        
    def load_data(self) -> pd.DataFrame:
        """Load data from Excel file"""
        try:
            self.data = pd.read_excel(self.filepath, sheet_name='Export')
            self.total_devices = len(self.data)
            print(f"Successfully loaded {self.total_devices:,} devices from {self.filepath.name}")
            return self.data
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    
    def analyze_esol_categories(self) -> Dict[str, int]:
        """Analyze ESOL device categories"""
        if self.data is None:
            self.load_data()
        if self.data is None:
            raise ValueError("Data not loaded")
        # Count ESOL categories
        action_counts = self.data['Action to take'].value_counts().to_dict()
        
        esol_2024 = action_counts.get('Urgent Replacement', 0)
        esol_2025 = action_counts.get('Replace by 14/10/2025', 0)
        total_esol = esol_2024 + esol_2025
        
        results = {
            'esol_2024_count': esol_2024,
            'esol_2025_count': esol_2025,
            'total_esol_count': total_esol,
            'esol_2024_percentage': (esol_2024 / self.total_devices) * 100,
            'esol_2025_percentage': (esol_2025 / self.total_devices) * 100,
            'total_esol_percentage': (total_esol / self.total_devices) * 100,
            'action_distribution': action_counts
        }
        
        return results
    
    def analyze_windows11_status(self) -> Dict[str, float]:
        """Analyze Windows 11 compatibility and adoption"""
        if self.data is None:
            self.load_data()
        if self.data is None:
            raise ValueError("Data not loaded")
        
        # Count Windows 11 devices
        win11_devices = self.data[self.data['Current OS Build'].str.contains('Win11', na=False)].shape[0]
        
        # Count Enterprise vs LTSC
        enterprise_count = self.data[self.data['LTSC or Enterprise'] == 'Enterprise'].shape[0]
        ltsc_count = self.data[self.data['LTSC or Enterprise'] == 'LTSC'].shape[0]
        
        # Calculate ESOL counts for compatibility
        esol_data = self.analyze_esol_categories()
        total_esol = esol_data['total_esol_count']
        compatible_devices = self.total_devices - total_esol
        
        results = {
            'win11_devices': win11_devices,
            'win11_adoption_percentage': (win11_devices / self.total_devices) * 100,
            'enterprise_devices': enterprise_count,
            'ltsc_devices': ltsc_count,
            'enterprise_percentage': (enterprise_count / self.total_devices) * 100,
            'compatible_devices': compatible_devices,
            'compatibility_percentage': (compatible_devices / self.total_devices) * 100,
            'win11_enterprise_adoption': (win11_devices / enterprise_count) * 100 if enterprise_count > 0 else 0
        }
        
        return results
    
    def analyze_kiosk_devices(self) -> Dict[str, int]:
        """Analyze kiosk devices based on user accounts containing GID or Kiosk"""
        if self.data is None:
            self.load_data()
        if self.data is None:
            raise ValueError("Data not loaded")
        
        # Check for kiosk indicators in user fields
        current_user_kiosk = self.data['Current User Logged On'].str.contains('gid|kiosk', case=False, na=False)
        last_user_kiosk = self.data['Last User Logged On'].str.contains('gid|kiosk', case=False, na=False)
        
        # Combine both conditions
        kiosk_mask = current_user_kiosk | last_user_kiosk
        kiosk_devices = self.data[kiosk_mask]
        
        # Count Enterprise kiosks that need re-provisioning
        enterprise_kiosks = kiosk_devices[kiosk_devices['LTSC or Enterprise'] == 'Enterprise'].shape[0]
        ltsc_kiosks = kiosk_devices[kiosk_devices['LTSC or Enterprise'] == 'LTSC'].shape[0]
        
        results = {
            'total_kiosk_devices': len(kiosk_devices),
            'enterprise_kiosks': enterprise_kiosks,
            'ltsc_kiosks': ltsc_kiosks,
            'kiosk_percentage': (len(kiosk_devices) / self.total_devices) * 100
        }
        
        return results
    
    def analyze_by_site(self) -> Dict[str, Dict[str, int]]:
        """Analyze ESOL devices by site location"""
        if self.data is None:
            self.load_data()
        if self.data is None:
            raise ValueError("Data not loaded")
        
        # Filter ESOL devices
        # Use boolean Series directly for masking
        esol_2024_mask = self.data['Action to take'] == 'Urgent Replacement'
        esol_2025_mask = self.data['Action to take'] == 'Replace by 14/10/2025'
        # Explicitly convert to Series for linter clarity
        esol_2024_by_site = pd.Series(self.data[esol_2024_mask]['Site Location']).value_counts().to_dict()
        esol_2025_by_site = pd.Series(self.data[esol_2025_mask]['Site Location']).value_counts().to_dict()
        
        # Combine site data
        all_sites = set(list(esol_2024_by_site.keys()) + list(esol_2025_by_site.keys()))
        
        site_analysis = {}
        for site in all_sites:
            esol_2024_count = esol_2024_by_site.get(site, 0)
            esol_2025_count = esol_2025_by_site.get(site, 0)
            total_esol = esol_2024_count + esol_2025_count
            
            site_analysis[site] = {
                'esol_2024': esol_2024_count,
                'esol_2025': esol_2025_count,
                'total_esol': total_esol
            }
        
        # Sort by total ESOL devices
        sorted_sites = dict(sorted(site_analysis.items(), 
                                 key=lambda x: x[1]['total_esol'], 
                                 reverse=True))
        
        return sorted_sites
    
    def calculate_replacement_costs(self) -> Dict[str, float]:
        """Calculate replacement costs for ESOL devices"""
        if self.data is None:
            self.load_data()
        if self.data is None:
            raise ValueError("Data not loaded")
        
        # Filter ESOL devices and calculate costs
        esol_2024_mask = self.data['Action to take'] == 'Urgent Replacement'
        esol_2025_mask = self.data['Action to take'] == 'Replace by 14/10/2025'
        
        esol_2024_cost = self.data[esol_2024_mask]['Cost for Replacement $'].sum()
        esol_2025_cost = self.data[esol_2025_mask]['Cost for Replacement $'].sum()
        total_cost = esol_2024_cost + esol_2025_cost
        
        results = {
            'esol_2024_cost': esol_2024_cost,
            'esol_2025_cost': esol_2025_cost,
            'total_replacement_cost': total_cost
        }
        
        return results
    
    def analyze_os_distribution(self) -> Dict[str, int]:
        """Analyze operating system distribution"""
        if self.data is None:
            self.load_data()
        if self.data is None:
            raise ValueError("Data not loaded")
        os_distribution = self.data['Current OS Build'].value_counts().to_dict()
        return os_distribution
    
    def calculate_okr_metrics(self) -> Dict[str, float]:
        """Calculate OKR-specific metrics"""
        esol_data = self.analyze_esol_categories()
        win11_data = self.analyze_windows11_status()
        kiosk_data = self.analyze_kiosk_devices()
        
        # Calculate 50% milestone for ESOL 2025
        esol_2025_50_percent_target = esol_data['esol_2025_count'] / 2
        esol_2025_50_percent_percentage = (esol_2025_50_percent_target / self.total_devices) * 100
        
        okr_metrics = {
            # KR1: ESOL 2024
            'kr1_current_percentage': esol_data['esol_2024_percentage'],
            'kr1_devices_remaining': esol_data['esol_2024_count'],
            
            # KR2: ESOL 2025
            'kr2_current_percentage': esol_data['esol_2025_percentage'],
            'kr2_50_percent_target': esol_2025_50_percent_percentage,
            'kr2_devices_for_50_percent': int(esol_2025_50_percent_target),
            'kr2_total_devices': esol_data['esol_2025_count'],
            
            # KR3: Windows 11 Compatibility
            'kr3_compatibility_percentage': win11_data['compatibility_percentage'],
            'kr3_adoption_percentage': win11_data['win11_adoption_percentage'],
            'kr3_target_met': win11_data['compatibility_percentage'] >= 90,
            
            # KR4: Kiosk re-provisioning
            'kr4_enterprise_kiosks': kiosk_data['enterprise_kiosks'],
            
            # Overall metrics
            'total_devices': self.total_devices,
            'total_esol_devices': esol_data['total_esol_count'],
            'total_esol_percentage': esol_data['total_esol_percentage']
        }
        
        return okr_metrics
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        if self.data is None:
            self.load_data()
        
        esol_data = self.analyze_esol_categories()
        win11_data = self.analyze_windows11_status()
        kiosk_data = self.analyze_kiosk_devices()
        site_data = self.analyze_by_site()
        cost_data = self.calculate_replacement_costs()
        okr_metrics = self.calculate_okr_metrics()
        
        report = f"""
# ESOL Data Analysis Report
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
File: {self.filepath.name}

## Summary Statistics
- **Total Devices**: {self.total_devices:,}
- **Total ESOL Devices**: {esol_data['total_esol_count']:,} ({esol_data['total_esol_percentage']:.2f}%)
- **Windows 11 Adoption**: {win11_data['win11_devices']:,} ({win11_data['win11_adoption_percentage']:.2f}%)

## OKR Key Results Status

### KR1: ESOL 2024 Remediation (Target: 0% by June 30, 2025)
- **Current**: {esol_data['esol_2024_count']} devices ({esol_data['esol_2024_percentage']:.2f}%)
- **Status**: AT RISK (0% progress)

### KR2: ESOL 2025 Remediation (Target: 0% by Dec 31, 2025)
- **Current**: {esol_data['esol_2025_count']} devices ({esol_data['esol_2025_percentage']:.2f}%)
- **50% Milestone**: {okr_metrics['kr2_devices_for_50_percent']} devices need remediation by June 30
- **Status**: CAUTION (0% progress)

### KR3: Windows 11 Compatibility (Target: >=90%)
- **Current**: {win11_data['compatibility_percentage']:.1f}%
- **Status**: {"ON TRACK" if okr_metrics['kr3_target_met'] else "CAUTION"}

### KR4: Kiosk Re-provisioning
- **Enterprise Kiosks**: {kiosk_data['enterprise_kiosks']} devices need LTSC re-provisioning

## Top 5 Sites Requiring ESOL Remediation
"""
        
        # Add top 5 sites
        top_sites = list(site_data.items())[:5]
        for i, (site, counts) in enumerate(top_sites, 1):
            report += f"{i}. **{site}**: {counts['total_esol']} total ({counts['esol_2024']} ESOL 2024, {counts['esol_2025']} ESOL 2025)\n"
        
        report += f"""
## Cost Analysis
- **ESOL 2024 Replacement Cost**: ${cost_data['esol_2024_cost']:,.0f}
- **ESOL 2025 Replacement Cost**: ${cost_data['esol_2025_cost']:,.0f}
- **Total Replacement Cost**: ${cost_data['total_replacement_cost']:,.0f}

## Device Distribution
- **Enterprise Devices**: {win11_data['enterprise_devices']:,} ({win11_data['enterprise_percentage']:.1f}%)
- **LTSC Devices**: {win11_data['ltsc_devices']:,}
- **Kiosk Devices**: {kiosk_data['total_kiosk_devices']:,} ({kiosk_data['kiosk_percentage']:.1f}%)

## Recommendations
1. **Immediate Action**: Procure replacements for all {esol_data['esol_2024_count']} ESOL 2024 devices
2. **Site Focus**: Prioritize {top_sites[0][0]} and {top_sites[1][0] if len(top_sites) > 1 else 'other high-count sites'}
3. **Budget Planning**: Allocate ${cost_data['total_replacement_cost']:,.0f} for all ESOL replacements
4. **Kiosk Strategy**: Re-provision {kiosk_data['enterprise_kiosks']} Enterprise kiosk devices to LTSC
"""
        
        return report

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Analyze ESOL device data for OKR tracking')
    add_data_file_argument(parser, 'Path to the Excel file containing device data')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    parser.add_argument('--json', action='store_true', help='Output metrics as JSON')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    data_file = get_data_file_path(args.data_file)
    validate_data_file(data_file)
    analyzer = ESOLAnalyzer(data_file)
    
    try:
        # Load and analyze data
        analyzer.load_data()
        
        if args.json:
            # Output JSON metrics
            import json
            metrics = analyzer.calculate_okr_metrics()
            json_output = json.dumps(metrics, indent=2)
            
            if args.output:
                # Save JSON to user-specified file
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_output)
                print(f"JSON metrics saved to {args.output}")
            else:
                # Auto-save JSON to data/reports/
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = Path('data/reports')
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = output_dir / f'ESOL_Metrics_{timestamp}.json'
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(json_output)
                print(f"JSON metrics auto-saved to {filename}")
                print(json_output)
        else:
            # Generate and display report
            report = analyzer.generate_report()
            
            if args.output:
                # Save to user-specified file
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"Report saved to {args.output}")
            else:
                # Auto-save to data/reports/
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = Path('data/reports')
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = output_dir / f'ESOL_Analysis_{timestamp}.md'
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"Report auto-saved to {filename}")
                # Print to console
                print(report)
                
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

# Example usage functions
def quick_analysis_example():
    """Example of how to use the analyzer for quick analysis"""
    # Initialize analyzer
    analyzer = ESOLAnalyzer('data/raw/EUC_ESOL.xlsx')
    
    # Load data
    analyzer.load_data()
    
    # Get OKR metrics
    metrics = analyzer.calculate_okr_metrics()
    
    print(f"ESOL 2024: {metrics['kr1_devices_remaining']} devices ({metrics['kr1_current_percentage']:.2f}%)")
    print(f"ESOL 2025: {metrics['kr2_total_devices']} devices ({metrics['kr2_current_percentage']:.2f}%)")
    print(f"Win11 Compatibility: {metrics['kr3_compatibility_percentage']:.1f}%")
    print(f"Win11 Adoption: {metrics['kr3_adoption_percentage']:.1f}%")

def site_analysis_example():
    """Example of site-specific analysis"""
    analyzer = ESOLAnalyzer('EUC_ESOL 2.xlsx')
    analyzer.load_data()
    
    site_data = analyzer.analyze_by_site()
    
    print("Top sites requiring ESOL remediation:")
    for site, counts in list(site_data.items())[:5]:
        print(f"- {site}: {counts['total_esol']} devices")

if __name__ == "__main__":
    main()