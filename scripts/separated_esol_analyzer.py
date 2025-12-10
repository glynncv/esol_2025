#!/usr/bin/env python3
"""
Truly Separated ESOL Data Analysis System
Clean separation: Data Analysis → Business Logic → Presentation

Requirements:
    pip install pandas openpyxl pyyaml

Usage Examples:
    # Quick status check (recommended for daily use)
    python separated_esol_analyzer.py --format quick
    
    # Executive summary (for management reports)
    python separated_esol_analyzer.py --format executive
    
    # Full OKR tracker (comprehensive report)
    python separated_esol_analyzer.py --format full
    
    # Site analysis (top priority sites)
    python separated_esol_analyzer.py --format site --top-sites 10
    
    # JSON output (for APIs or further processing)
    python separated_esol_analyzer.py --format json
    
    # Save to file
    python separated_esol_analyzer.py --format executive -o reports/weekly_update.md
"""

import pandas as pd
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
import argparse
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file

# Fix UTF-8 encoding for Windows console to handle emoji characters
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: str = "config/"):
        self.config_path = Path(config_path)
        self.esol_config = self._load_yaml("esol_criteria.yaml")
        self.okr_config = self._load_yaml("okr_criteria.yaml")
        self.win11_config = self._load_yaml("win11_criteria.yaml")
        self.validate_config()
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        file_path = self.config_path / filename

        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {file_path}")
            print(f"Creating default configuration...")
            self._create_default_config(filename)
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ Error loading {filename}: {e}")
            sys.exit(1)
    
    def _create_default_config(self, filename: str):
        """Create default configuration files if they don't exist"""
        self.config_path.mkdir(exist_ok=True)
        
        if filename == "esol_criteria.yaml":
            default_config = {
                'esol_categories': {
                    'esol_2024': {
                        'action_value': 'Urgent Replacement',
                        'target_date': '2025-06-30',
                        'description': 'Critical devices requiring immediate replacement'
                    },
                    'esol_2025': {
                        'action_value': 'Replace by 14/10/2025',
                        'target_date': '2025-10-14',
                        'description': 'Devices to be replaced by October 2025'
                    },
                    'esol_2026': {
                        'action_value': 'Replace by 11/11/2026',
                        'target_date': '2026-11-11',
                        'description': 'Future replacement devices'
                    }
                },
                'data_mapping': {
                    'action_column': 'Action to take',
                    'os_column': 'Current OS Build',
                    'edition_column': 'LTSC or Enterprise',
                    'cost_column': 'Cost for Replacement $',
                    'site_column': 'Site Location',
                    'user_columns': {
                        'current': 'Current User Logged On',
                        'last': 'Last User Logged On'
                    }
                },
                'kiosk_detection': {
                    'patterns': ['gid', 'kiosk'],
                    'case_sensitive': False,
                    'logic': 'OR'
                },
            }
        
        elif filename == "okr_criteria.yaml":
            default_config = {
                'okr_weights': {
                    'kr1_esol_2024': 25,
                    'kr2_esol_2025': 25,
                    'kr3_win11_compatibility': 40,
                    'kr4_kiosk_reprovisioning': 10
                },
                'status_levels': {
                    'at_risk': 0,
                    'caution': 1,
                    'on_track': 2
                },
                'status_thresholds': {
                    'on_track_min_progress': 80,
                    'caution_min_progress': 60
                },
                'targets': {
                    'kr1_target_percentage': 0,
                    'kr2_target_percentage': 0,
                    'kr2_milestone_percentage': 50,
                    'kr3_target_percentage': 90,
                    'kr4_target_count': 0
                },
                'milestone_dates': {
                    'kr1_deadline': '2025-06-30',
                    'kr2_milestone_date': '2025-06-30',
                    'kr2_deadline': '2025-12-31',
                    'kr3_deadline': '2025-10-31',
                    'kr4_deadline': '2025-06-30'
                }
            }
        
        elif filename == "win11_criteria.yaml":
            default_config = {
                'kpi_target_date': '2025-10-31',
                'kpi_target_percentage': 100,
                'target_editions': ['Enterprise'],
                'exclude_editions': ['LTSC'],
                'excluded_actions': ['esol_2024', 'esol_2025'],
                'win11_patterns': ['Win11'],
                'migration_categories': ['esol_2024', 'esol_2025']
            }
        
        with open(self.config_path / filename, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        print(f"✅ Created default config: {self.config_path / filename}")
    
    def get_esol_criteria(self) -> Dict[str, Any]:
        return self.esol_config
    
    def get_okr_criteria(self) -> Dict[str, Any]:
        return self.okr_config
    
    def get_win11_criteria(self) -> Dict[str, Any]:
        return self.win11_config
    
    def validate_config(self) -> bool:
        """Validate configuration completeness and consistency"""
        required_esol_keys = ['esol_categories', 'data_mapping', 'kiosk_detection']
        required_okr_keys = ['okr_weights', 'status_levels', 'targets', 'milestone_dates']
        required_win11_keys = ['kpi_target_date', 'kpi_target_percentage', 'target_editions', 'excluded_actions', 'win11_patterns']
        
        for key in required_esol_keys:
            if key not in self.esol_config:
                raise ValueError(f"Missing required ESOL config key: {key}")
        
        for key in required_okr_keys:
            if key not in self.okr_config:
                raise ValueError(f"Missing required OKR config key: {key}")
        
        for key in required_win11_keys:
            if key not in self.win11_config:
                raise ValueError(f"Missing required Windows 11 config key: {key}")
        
        # Validate weight percentages sum to 100
        weights = self.okr_config['okr_weights']
        total_weight = sum(weights.values())
        if total_weight != 100:
            print(f"⚠️  Warning: OKR weights sum to {total_weight}%, not 100%")
        
        return True


# DELETED: DataAnalyzer, BusinessLogicCalculator, PresentationFormatter classes (619 lines)
# These classes duplicated functionality from modern ETL modules:
# - DataAnalyzer → etl/load_data.py (DataLoader)
# - BusinessLogicCalculator → etl/analysis/* (ESOLAnalyzer, Win11Analyzer, OKRAggregator)
# - PresentationFormatter → etl/presentation/* (OKRFormatter, formatters)
# See git history for original implementation


class OKRAnalysisOrchestrator:
    """Thin compatibility wrapper around modern ETL modules for backward compatibility.

    This class maintains the API used by okr_dashboard.py while using the modern
    ETL architecture internally. All business logic has been moved to etl/ modules.
    """

    def __init__(self, config_path: str = "config/"):
        """Initialize with modern ETL modules"""
        # Import ETL modules (lazy import to avoid circular dependencies)
        from etl.load_data import DataLoader
        from etl.analysis.esol_analyzer import ESOLAnalyzer
        from etl.analysis.win11_analyzer import Win11Analyzer
        from etl.analysis.kiosk_analyzer import KioskAnalyzer
        from etl.analysis.okr_aggregator import OKRAggregator

        # Initialize config and modern ETL modules
        self.config = ConfigManager(config_path)
        self.data_loader = DataLoader(self.config)
        self.esol_analyzer = ESOLAnalyzer(self.config)
        self.win11_analyzer = Win11Analyzer(self.config)
        self.kiosk_analyzer = KioskAnalyzer(self.config)
        self.okr_aggregator = OKRAggregator(self.config)

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Complete analysis pipeline using modern ETL modules.

        Returns metrics dict compatible with legacy okr_dashboard.py expectations.
        """
        # Load data using modern DataLoader
        df = self.data_loader.load_raw_data(filepath)

        # Run modern analyzers
        esol_counts = self.esol_analyzer.calculate_esol_counts(df)

        # Filter for Enterprise devices for Win11 analysis
        enterprise_df = self.data_loader.filter_enterprise_devices(df)
        win11_counts = self.win11_analyzer.calculate_win11_counts(enterprise_df)

        # Filter for kiosk devices
        kiosk_df = self.data_loader.filter_kiosk_devices(df)
        kiosk_counts = self.kiosk_analyzer.calculate_kiosk_counts(kiosk_df, len(df))

        # Calculate OKR scores using modern aggregator
        okr_scores = self.okr_aggregator.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)

        # Extract site analysis data (for site_analysis method)
        site_data = self._extract_site_data(df)

        # Map modern ETL output to legacy format expected by okr_dashboard.py
        # okr_dashboard.py expects these specific keys for quick_status()
        return {
            # Overall metrics
            'total_devices': esol_counts['total_devices'],
            'overall_score': okr_scores['okr_score'],
            'overall_status_level': self._map_status_to_level(okr_scores['status']),

            # ESOL counts and percentages
            'esol_2024_count': esol_counts.get('esol_2024', 0),
            'esol_2024_percentage': esol_counts.get('esol_2024', 0) / esol_counts['total_devices'] * 100 if esol_counts['total_devices'] > 0 else 0,
            'esol_2025_count': esol_counts.get('esol_2025', 0),
            'esol_2025_percentage': esol_counts.get('esol_2025', 0) / esol_counts['total_devices'] * 100 if esol_counts['total_devices'] > 0 else 0,

            # Windows 11 metrics
            'win11_count': win11_counts.get('win11_count', 0),
            'win11_percentage': win11_counts.get('win11_adoption_pct', 0),
            'compatibility_percentage': win11_counts.get('win11_adoption_pct', 0),
            'compatible_device_count': int(esol_counts['total_devices'] * win11_counts.get('win11_adoption_pct', 0) / 100),

            # Kiosk metrics
            'enterprise_kiosk_count': kiosk_counts.get('enterprise_count', 0),

            # KR scores and status
            'kr1_progress_score': okr_scores['kr1_score'],
            'kr1_status_level': self._map_kr_status_to_level(okr_scores['kr1_score']),
            'kr1_weighted_score': okr_scores['kr1_score'] * 0.25,  # 25% weight
            'kr2_progress_score': okr_scores['kr2_score'],
            'kr2_status_level': self._map_kr_status_to_level(okr_scores['kr2_score']),
            'kr2_weighted_score': okr_scores['kr2_score'] * 0.25,  # 25% weight
            'kr3_progress_score': okr_scores['kr3_score'],
            'kr3_status_level': self._map_kr_status_to_level(okr_scores['kr3_score']),
            'kr3_weighted_score': okr_scores['kr3_score'] * 0.40,  # 40% weight
            'kr4_progress_score': okr_scores['kr4_score'],
            'kr4_status_level': self._map_kr_status_to_level(okr_scores['kr4_score']),
            'kr4_weighted_score': okr_scores['kr4_score'] * 0.10,  # 10% weight

            # Milestone metrics (for KR2)
            'kr2_milestone_target_devices': int(esol_counts.get('esol_2025', 0) * 0.5),
            'kr2_milestone_target_percentage': esol_counts.get('esol_2025', 0) / esol_counts['total_devices'] * 50 if esol_counts['total_devices'] > 0 else 0,
            'kr2_milestone_progress_score': 0.0,

            # Site data for site analysis
            'site_data': site_data
        }

    def _map_status_to_level(self, status: str) -> int:
        """Map status string to numeric level (0=AT RISK, 1=CAUTION, 2=ON TRACK)"""
        status_map = {
            'AT RISK': 0,
            'CAUTION': 1,
            'ON TRACK': 2
        }
        return status_map.get(status, 0)

    def _map_kr_status_to_level(self, kr_score: float) -> int:
        """Map KR score to status level"""
        if kr_score >= 80:
            return 2  # ON TRACK
        elif kr_score >= 60:
            return 1  # CAUTION
        else:
            return 0  # AT RISK

    def _extract_site_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        """Extract site-level ESOL counts for site analysis"""
        action_col = self.config.get_esol_criteria()['data_mapping']['action_column']
        site_col = self.config.get_esol_criteria()['data_mapping']['site_column']
        esol_categories = self.config.get_esol_criteria()['esol_categories']

        site_counts = {}

        for category, criteria in esol_categories.items():
            esol_devices = df[df[action_col] == criteria['action_value']]
            for site in esol_devices[site_col].dropna().unique():
                if site not in site_counts:
                    site_counts[site] = {cat: 0 for cat in esol_categories.keys()}

                count = len(esol_devices[esol_devices[site_col] == site])
                site_counts[site][category] = count

        return site_counts

    def generate_full_report(self, filepath: str) -> str:
        """Generate complete OKR tracking report using legacy formatter"""
        metrics = self.analyze_file(filepath)
        return self._format_okr_tracker(metrics)

    def generate_executive_summary(self, filepath: str) -> str:
        """Generate executive summary using legacy formatter"""
        metrics = self.analyze_file(filepath)
        return self._format_executive_summary(metrics)

    def generate_site_analysis(self, filepath: str, top_n: int = 5) -> str:
        """Generate site-level analysis using legacy formatter"""
        metrics = self.analyze_file(filepath)
        return self._format_site_analysis(metrics['site_data'], top_n)

    def get_metrics_json(self, filepath: str) -> Dict[str, Any]:
        """Get raw metrics as JSON for API integration"""
        return self.analyze_file(filepath)

    def _format_executive_summary(self, metrics: Dict[str, Any]) -> str:
        """Simple executive summary format for okr_dashboard.py"""
        status_emoji = ['🔴', '🟡', '🟢'][metrics['overall_status_level']]
        status_text = ['AT RISK', 'CAUTION', 'ON TRACK'][metrics['overall_status_level']]

        return f"""# Executive Summary - Technical Debt Remediation OKR

**Overall Status: {status_emoji} {status_text} ({metrics['overall_score']:.1f}%)**

## Key Highlights
- **ESOL 2024**: {metrics['esol_2024_count']} devices require immediate replacement
- **Windows 11 Compatibility**: {metrics['compatibility_percentage']:.1f}% achieved (target: 90%)
- **Total Investment Required**: Procurement needed for {metrics['total_devices'] - metrics['compatible_device_count']} devices

## Critical Actions Required
1. **Immediate**: Procure {metrics['esol_2024_count']} ESOL 2024 devices by June 30
2. **Q3 Focus**: Plan {metrics['kr2_milestone_target_devices']} ESOL 2025 device replacements
3. **Kiosk Remediation**: Re-provision {metrics['enterprise_kiosk_count']} Enterprise kiosk devices to LTSC

## Progress by Key Result
- **KR1 (25%)**: {['🔴', '🟡', '🟢'][metrics['kr1_status_level']]} {metrics['kr1_weighted_score']:.1f}% weighted
- **KR2 (25%)**: {['🔴', '🟡', '🟢'][metrics['kr2_status_level']]} {metrics['kr2_weighted_score']:.1f}% weighted
- **KR3 (40%)**: {['🔴', '🟡', '🟢'][metrics['kr3_status_level']]} {metrics['kr3_weighted_score']:.1f}% weighted
- **KR4 (10%)**: {['🔴', '🟡', '🟢'][metrics['kr4_status_level']]} {metrics['kr4_weighted_score']:.1f}% weighted
"""

    def _format_okr_tracker(self, metrics: Dict[str, Any]) -> str:
        """Full OKR tracker format - simplified version"""
        today = datetime.now().strftime('%Y-%m-%d')
        status_emoji = ['🔴', '🟡', '🟢'][metrics['overall_status_level']]
        status_text = ['AT RISK', 'CAUTION', 'ON TRACK'][metrics['overall_status_level']]

        return f"""# Technical Debt Remediation OKR Tracker
*Date of Review: {today}*

## Overall Status: {status_emoji} {status_text} ({metrics['overall_score']:.1f}%)

## Key Results Summary

### KR1: ESOL 2024 Remediation
- **Current**: {metrics['esol_2024_count']} devices ({metrics['esol_2024_percentage']:.2f}%)
- **Target**: 0 devices (0%)
- **Progress**: {metrics['kr1_progress_score']:.0f}%
- **Status**: {['🔴 AT RISK', '🟡 CAUTION', '🟢 ON TRACK'][metrics['kr1_status_level']]}

### KR2: ESOL 2025 Remediation
- **Current**: {metrics['esol_2025_count']} devices ({metrics['esol_2025_percentage']:.2f}%)
- **Target**: 0 devices (0%)
- **Progress**: {metrics['kr2_progress_score']:.0f}%
- **Status**: {['🔴 AT RISK', '🟡 CAUTION', '🟢 ON TRACK'][metrics['kr2_status_level']]}

### KR3: Windows 11 Compatibility
- **Current**: {metrics['compatibility_percentage']:.1f}%
- **Target**: 90%
- **Progress**: {metrics['kr3_progress_score']:.0f}%
- **Status**: {['🔴 AT RISK', '🟡 CAUTION', '🟢 ON TRACK'][metrics['kr3_status_level']]}

### KR4: Kiosk Re-provisioning
- **Current**: {metrics['enterprise_kiosk_count']} devices
- **Target**: 0 devices
- **Progress**: {metrics['kr4_progress_score']:.0f}%
- **Status**: {['🔴 AT RISK', '🟡 CAUTION', '🟢 ON TRACK'][metrics['kr4_status_level']]}

## Fleet Composition
- Total Devices: {metrics['total_devices']:,}
- ESOL 2024: {metrics['esol_2024_count']} devices ({metrics['esol_2024_percentage']:.2f}%)
- ESOL 2025: {metrics['esol_2025_count']} devices ({metrics['esol_2025_percentage']:.2f}%)
- Windows 11 Compatible: {metrics['compatible_device_count']:,} devices ({metrics['compatibility_percentage']:.1f}%)
"""

    def _format_site_analysis(self, site_data: Dict[str, Dict[str, int]], top_n: int = 5) -> str:
        """Site analysis format"""
        sorted_sites = sorted(site_data.items(),
                            key=lambda x: sum(x[1].values()),
                            reverse=True)

        analysis = f"""# Site-Level ESOL Analysis
## Top {top_n} Sites Requiring ESOL Remediation

"""

        for i, (site, counts) in enumerate(sorted_sites[:top_n], 1):
            total_esol = sum(counts.values())
            esol_2024 = counts.get('esol_2024', 0)
            esol_2025 = counts.get('esol_2025', 0)

            analysis += f"""### {i}. {site}
- **Total ESOL Devices**: {total_esol}
- **ESOL 2024 (Urgent)**: {esol_2024} devices
- **ESOL 2025**: {esol_2025} devices
- **Priority**: {'🔴 CRITICAL' if esol_2024 > 20 else '🟡 HIGH' if total_esol > 50 else '🟢 MEDIUM'}

"""

        return analysis