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


class DataAnalyzer:
    """PURE data analysis layer - only extracts and counts, no business logic or formatting"""
    
    def __init__(self, config: ConfigManager):
        self.config = config.get_esol_criteria()
        self.win11_config = config.get_win11_criteria()
        self.data_mapping = self.config['data_mapping']
        self.esol_categories = self.config['esol_categories']
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load and validate data from Excel file"""
        try:
            # Handle relative paths from project root
            file_path = Path(filepath)
            if not file_path.is_absolute():
                # Try common locations
                possible_paths = [
                    file_path,  # As provided
                    Path('data/raw') / file_path,  # Project data folder
                    Path('../data/raw') / file_path,  # From scripts folder
                ]
                
                for path in possible_paths:
                    if path.exists():
                        file_path = path
                        break
                else:
                    raise FileNotFoundError(f"File not found in any location: {[str(p) for p in possible_paths]}")
            
            df = pd.read_excel(file_path, sheet_name='Export')
            self._validate_data_columns(df)
            print(f"✅ Loaded data from: {file_path}")
            return df
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            sys.exit(1)
    
    def _validate_data_columns(self, df: pd.DataFrame):
        """Validate that required columns exist in the dataframe"""
        required_columns = [
            self.data_mapping['action_column'],
            self.data_mapping['os_column'],
            self.data_mapping['edition_column'],
            self.data_mapping['site_column']
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Validate expected data types
        string_cols = [
            self.data_mapping['action_column'],
            self.data_mapping['os_column'],
            self.data_mapping['edition_column'],
            self.data_mapping['site_column'],
        ]
        numeric_cols = [self.data_mapping.get('cost_column')]

        for col in string_cols:
            if col in df.columns and not pd.api.types.is_object_dtype(df[col]):
                raise TypeError(f"Column '{col}' must contain string data")

        for col in numeric_cols:
            if col and col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(f"Column '{col}' must be numeric")

        # Validate allowed values and ranges
        edition_col = self.data_mapping['edition_column']
        if edition_col in df.columns:
            allowed_editions = {"Enterprise", "LTSC"}
            invalid = df.loc[~df[edition_col].isin(allowed_editions), edition_col].dropna().unique()
            if len(invalid) > 0:
                raise ValueError(f"Invalid values in '{edition_col}': {invalid}")

        cost_col = self.data_mapping.get('cost_column')
        if cost_col and cost_col in df.columns and pd.api.types.is_numeric_dtype(df[cost_col]):
            if (df[cost_col] < 0).any():
                raise ValueError(f"Negative values found in '{cost_col}'")
    
    def extract_basic_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract basic device counts - pure data extraction"""
        action_col = self.data_mapping['action_column']
        edition_col = self.data_mapping['edition_column']
        os_col = self.data_mapping['os_column']
        
        total_devices = len(df)
        
        # Count each ESOL category
        esol_counts = {}
        for category, criteria in self.esol_categories.items():
            count = len(df[df[action_col] == criteria['action_value']])
            esol_counts[f"{category}_count"] = count
        
        # Count editions
        enterprise_count = len(df[df[edition_col] == 'Enterprise'])
        ltsc_count = len(df[df[edition_col] == 'LTSC'])
        
        # Count Windows 11 devices (Enterprise focus for 2025 push)
        win11_patterns = '|'.join(self.win11_config['win11_patterns'])
        
        # Filter for Enterprise devices only (the 2025 Windows 11 push target)
        enterprise_mask = df[edition_col] == 'Enterprise'
        enterprise_df = df[enterprise_mask]
        
        # Count Enterprise devices already on Windows 11
        enterprise_win11_count = len(enterprise_df[enterprise_df[os_col].str.contains(win11_patterns, na=False)])
        
        # Count Enterprise devices that will get Windows 11 via ESOL replacement
        migration_categories = self.win11_config['migration_categories']
        migration_actions = [self.esol_categories[cat]['action_value'] for cat in migration_categories]
        enterprise_esol_mask = enterprise_df[action_col].isin(migration_actions)
        enterprise_esol_count = len(enterprise_df[enterprise_esol_mask])
        
        # Calculate Enterprise Windows 11 adoption path
        total_enterprise_win11_path = enterprise_win11_count + enterprise_esol_count
        enterprise_win11_adoption_pct = (total_enterprise_win11_path / len(enterprise_df)) * 100 if len(enterprise_df) > 0 else 0
        
        return {
            'total_devices': total_devices,
            **esol_counts,
            'enterprise_count': enterprise_count,
            'ltsc_count': ltsc_count,
            'win11_count': enterprise_win11_count,  # Enterprise devices already on Win11
            'enterprise_win11_adoption_count': total_enterprise_win11_path,
            'enterprise_win11_adoption_percentage': enterprise_win11_adoption_pct,
            'enterprise_esol_count': enterprise_esol_count
        }
    
    def extract_kiosk_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract kiosk device counts - pure data extraction"""
        kiosk_config = self.config['kiosk_detection']
        user_mapping = self.data_mapping['user_columns']
        edition_col = self.data_mapping['edition_column']
        device_name_col = self.data_mapping['device_name_column']
        
        # Get patterns for device name and user fields
        device_patterns = '|'.join(kiosk_config['device_name_patterns'])
        user_patterns = '|'.join(kiosk_config['user_loggedon_patterns'])
        case_sensitive = kiosk_config['case_sensitive']
        
        # Check device name for kiosk patterns
        device_mask = df[device_name_col].str.contains(
            device_patterns, case=case_sensitive, na=False)
        
        # Check user fields for kiosk patterns
        current_mask = df[user_mapping['current']].str.contains(
            user_patterns, case=case_sensitive, na=False)
        last_mask = df[user_mapping['last']].str.contains(
            user_patterns, case=case_sensitive, na=False)
        
        # Apply logic (OR/AND) for user fields
        if kiosk_config['logic'].upper() == 'OR':
            user_mask = current_mask | last_mask
        else:  # AND logic
            user_mask = current_mask & last_mask
        
        # Combine device name and user patterns with OR logic
        kiosk_mask = device_mask | user_mask
        
        kiosk_devices = df[kiosk_mask]
        
        # Count by edition
        enterprise_kiosks = len(kiosk_devices[kiosk_devices[edition_col] == 'Enterprise'])
        ltsc_kiosks = len(kiosk_devices[kiosk_devices[edition_col] == 'LTSC'])
        
        return {
            'total_kiosk_count': len(kiosk_devices),
            'enterprise_kiosk_count': enterprise_kiosks,
            'ltsc_kiosk_count': ltsc_kiosks
        }
    
    def extract_site_counts(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        """Extract ESOL device counts by site - pure data extraction"""
        action_col = self.data_mapping['action_column']
        site_col = self.data_mapping['site_column']
        
        site_counts = {}
        
        # Get all sites that have ESOL devices
        for category, criteria in self.esol_categories.items():
            esol_devices = df[df[action_col] == criteria['action_value']]
            for site in esol_devices[site_col].dropna().unique():
                if site not in site_counts:
                    site_counts[site] = {cat: 0 for cat in self.esol_categories.keys()}
                
                count = len(esol_devices[esol_devices[site_col] == site])
                site_counts[site][category] = count
        
        return site_counts
    
    def extract_cost_totals(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract replacement cost totals - pure data extraction"""
        action_col = self.data_mapping['action_column']
        cost_col = self.data_mapping['cost_column']
        
        costs = {}
        
        for category, criteria in self.esol_categories.items():
            esol_devices = df[df[action_col] == criteria['action_value']]
            category_cost = esol_devices[cost_col].fillna(0).sum()
            costs[f"{category}_cost"] = float(category_cost)
        
        return costs


class BusinessLogicCalculator:
    """PURE business logic layer - only calculations and numeric indicators"""
    
    def __init__(self, config: ConfigManager):
        self.okr_config = config.get_okr_criteria()
        self.esol_config = config.get_esol_criteria()
        self.win11_config = config.get_win11_criteria()
        self.weights = self.okr_config['okr_weights']
        self.targets = self.okr_config['targets']
        self.status_levels = self.okr_config['status_levels']
        self.thresholds = self.okr_config['status_thresholds']
    
    def calculate_percentages(self, raw_counts: Dict[str, int]) -> Dict[str, float]:
        """Calculate all percentages from raw counts"""
        total = raw_counts['total_devices']
        if total == 0:
            return {key.replace('_count', '_percentage'): 0.0 for key in raw_counts if key.endswith('_count')}
        
        percentages = {}
        for key, count in raw_counts.items():
            if key.endswith('_count') and key != 'total_devices':
                pct_key = key.replace('_count', '_percentage')
                percentages[pct_key] = (count / total) * 100
        
        return percentages
    
    def calculate_windows11_compatibility(self, raw_counts: Dict[str, int]) -> Dict[str, float]:
        """Calculate Windows 11 compatibility based on configuration"""
        total_devices = raw_counts['total_devices']
        
        # Calculate Enterprise Windows 11 adoption path
        migration_categories = self.win11_config['migration_categories']
        enterprise_esol_count = sum(raw_counts[f"{cat}_count"] for cat in migration_categories)
        enterprise_win11_count = raw_counts['win11_count']
        
        compatible_count = enterprise_win11_count + enterprise_esol_count
        compatibility_percentage = (compatible_count / total_devices) * 100 if total_devices > 0 else 0
        
        return {
            'compatible_device_count': compatible_count,
            'enterprise_win11_count': enterprise_win11_count,
            'enterprise_esol_count': enterprise_esol_count,
            'compatibility_percentage': compatibility_percentage
        }
    
    def calculate_kr_progress_scores(self, raw_counts: Dict[str, int], percentages: Dict[str, float], 
                                   compatibility: Dict[str, float]) -> Dict[str, float]:
        """Calculate numeric progress scores for each Key Result (0-100)"""
        
        # KR1: ESOL 2024 - binary (0% target achieved = 100, anything else = 0)
        kr1_progress = 100.0 if percentages['esol_2024_percentage'] <= self.targets['kr1_target_percentage'] else 0.0
        
        # KR2: ESOL 2025 - binary (0% target achieved = 100, anything else = 0)  
        kr2_progress = 100.0 if percentages['esol_2025_percentage'] <= self.targets['kr2_target_percentage'] else 0.0
        
        # KR3: Windows 11 Compatibility - progressive (can be partial)
        kr3_current = compatibility['compatibility_percentage']
        kr3_target = self.targets['kr3_target_percentage']
        kr3_progress = min(100.0, (kr3_current / kr3_target) * 100) if kr3_target > 0 else 100.0
        
        # KR4: Kiosk Re-provisioning - binary (0 devices = 100, anything else = 0)
        kr4_progress = 100.0 if raw_counts['enterprise_kiosk_count'] <= self.targets['kr4_target_count'] else 0.0
        
        return {
            'kr1_progress_score': kr1_progress,
            'kr2_progress_score': kr2_progress,
            'kr3_progress_score': kr3_progress,
            'kr4_progress_score': kr4_progress
        }
    
    def calculate_weighted_scores(self, progress_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate weighted scores for each KR"""
        return {
            'kr1_weighted_score': progress_scores['kr1_progress_score'] * (self.weights['kr1_esol_2024'] / 100),
            'kr2_weighted_score': progress_scores['kr2_progress_score'] * (self.weights['kr2_esol_2025'] / 100),
            'kr3_weighted_score': progress_scores['kr3_progress_score'] * (self.weights['kr3_win11_compatibility'] / 100),
            'kr4_weighted_score': progress_scores['kr4_progress_score'] * (self.weights['kr4_kiosk_reprovisioning'] / 100)
        }
    
    def calculate_overall_score(self, weighted_scores: Dict[str, float]) -> float:
        """Calculate overall OKR completion score"""
        return sum(weighted_scores.values())
    
    def calculate_status_levels(self, progress_scores: Dict[str, float]) -> Dict[str, int]:
        """Calculate numeric status levels (0=at_risk, 1=caution, 2=on_track)"""
        status_levels = {}
        
        for kr in ['kr1', 'kr2', 'kr3', 'kr4']:
            score = progress_scores[f"{kr}_progress_score"]
            
            if score >= self.thresholds['on_track_min_progress']:
                status_levels[f"{kr}_status_level"] = self.status_levels['on_track']
            elif score >= self.thresholds['caution_min_progress']:
                status_levels[f"{kr}_status_level"] = self.status_levels['caution']
            else:
                status_levels[f"{kr}_status_level"] = self.status_levels['at_risk']
        
        # Overall status based on overall score
        overall_score = sum(progress_scores.values()) / 4  # Average of all KRs
        if overall_score >= self.thresholds['on_track_min_progress']:
            status_levels['overall_status_level'] = self.status_levels['on_track']
        elif overall_score >= self.thresholds['caution_min_progress']:
            status_levels['overall_status_level'] = self.status_levels['caution']
        else:
            status_levels['overall_status_level'] = self.status_levels['at_risk']
        
        return status_levels
    
    def calculate_milestone_metrics(self, raw_counts: Dict[str, int], percentages: Dict[str, float]) -> Dict[str, Union[int, float]]:
        """Calculate milestone-specific metrics"""
        # KR2 50% milestone calculations
        esol_2025_total = raw_counts['esol_2025_count']
        milestone_target_devices = int(esol_2025_total * (self.targets['kr2_milestone_percentage'] / 100))
        milestone_target_percentage = percentages['esol_2025_percentage'] * (self.targets['kr2_milestone_percentage'] / 100)
        
        return {
            'kr2_milestone_target_devices': milestone_target_devices,
            'kr2_milestone_target_percentage': milestone_target_percentage,
            'kr2_milestone_progress_score': 0.0  # Always 0 until milestone is achieved
        }


class PresentationFormatter:
    """PURE presentation layer - only formatting, no calculations"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.okr_config = config.get_okr_criteria()
        self.esol_config = config.get_esol_criteria()
        
        # Status level to text mapping
        self.status_text_map = {
            0: 'AT RISK',
            1: 'CAUTION', 
            2: 'ON TRACK'
        }
        
        # Status level to emoji mapping
        self.status_emoji_map = {
            0: '🔴',
            1: '🟡',
            2: '🟢'
        }
    
    def format_okr_tracker(self, all_metrics: Dict[str, Any]) -> str:
        """Generate complete OKR tracker markdown - pure formatting"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        tracker = f"""# Technical Debt Remediation OKR Tracker
*Date of Review: {today}*

## Objective: Eliminate high-risk technical debt to reduce operational cost and improve security posture.

"""
        
        tracker += self._format_kr1_section(all_metrics)
        tracker += self._format_kr2_section(all_metrics)
        tracker += self._format_kr3_section(all_metrics)
        tracker += self._format_kr4_section(all_metrics)
        tracker += self._format_dashboard_section(all_metrics)
        tracker += self._format_risk_section()
        
        return tracker
    
    def _format_kr1_section(self, metrics: Dict[str, Any]) -> str:
        """Format KR1 section - pure formatting"""
        esol_2024_config = self.esol_config['esol_categories']['esol_2024']
        target_date = esol_2024_config['target_date']
        
        current_pct = metrics['esol_2024_percentage']
        device_count = metrics['esol_2024_count']
        status_level = metrics['kr1_status_level']
        progress_score = metrics['kr1_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        progress_bar = self._generate_progress_bar(progress_score)
        
        return f"""### Key Result 1: Remediate 100% of 2024 ESOL equipment by {target_date} (📌)

| Metric | Target | Current | Gap | Deadline | Status |
|--------|--------|---------|-----|----------|--------|
| 2024 ESOL Percentage | 0% (0 devices) | {current_pct:.2f}% ({device_count} devices) | {device_count} devices | {target_date} | {status_emoji} {status_text} |

**Current ESOL 2024 Percentage:**
- 🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴 {current_pct:.2f}% (Target: 0%)

**Remediation Progress:**
- {progress_bar} {progress_score:.0f}% Complete

**Action Plan:**
- Immediate procurement for all {device_count} devices
- Establish site coordinators at all impacted locations
- Weekly status reviews until completion

---

"""
    
    def _format_kr2_section(self, metrics: Dict[str, Any]) -> str:
        """Format KR2 section - pure formatting"""
        esol_2025_config = self.esol_config['esol_categories']['esol_2025']
        target_date = esol_2025_config['target_date']
        milestone_date = self.okr_config['milestone_dates']['kr2_milestone_date']
        
        current_pct = metrics['esol_2025_percentage']
        device_count = metrics['esol_2025_count']
        milestone_target_devices = metrics['kr2_milestone_target_devices']
        milestone_target_pct = metrics['kr2_milestone_target_percentage']
        status_level = metrics['kr2_status_level']
        progress_score = metrics['kr2_progress_score']
        milestone_progress = metrics['kr2_milestone_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        progress_bar = self._generate_progress_bar(progress_score)
        milestone_progress_bar = self._generate_progress_bar(milestone_progress)
        
        return f"""### Key Result 2: Complete 50% of 2025 ESOL remediation by {milestone_date} and 100% by {target_date} (📌)

| Milestone | Target | Current | Gap | Deadline | Status |
|-----------|--------|---------|-----|----------|--------|
| 50% Milestone (ESOL %) | {milestone_target_pct:.2f}% ({milestone_target_devices} devices remaining) | {current_pct:.2f}% ({device_count} devices) | {milestone_target_devices} devices | {milestone_date} | {status_emoji} {status_text} |
| 100% Completion (ESOL %) | 0% (0 devices) | {current_pct:.2f}% ({device_count} devices) | {device_count} devices | {target_date} | {status_emoji} {status_text} |

**Current ESOL 2025 Percentage:**
- 🔴🔴🔴🔴🔴🔴🔴🔴🔴⬜ {current_pct:.2f}% (Target: 0% by {target_date})

**50% Milestone Progress (Target: {milestone_target_pct:.2f}% ESOL):**
- {milestone_progress_bar} {milestone_progress:.0f}% Complete (Need to remediate {milestone_target_devices} devices)

**Total Progress (Target: 0% ESOL):**
- {progress_bar} {progress_score:.0f}% Complete

**Action Plan:**
- Finalize procurement plan for Q2/Q3 to meet 50% June target
- Focus on high-density sites based on site analysis
- Ensure hardware compatibility with Windows 11 for all replacements

---

"""
    
    def _format_kr3_section(self, metrics: Dict[str, Any]) -> str:
        """Format KR3 section - pure formatting"""
        compatibility_pct = metrics['compatibility_percentage']
        win11_adoption_pct = metrics['win11_percentage']
        target_pct = self.okr_config['targets']['kr3_target_percentage']
        status_level = metrics['kr3_status_level']
        progress_score = metrics['kr3_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        compat_progress_bar = self._generate_progress_bar(progress_score)
        adoption_progress_bar = self._generate_progress_bar(win11_adoption_pct)
        
        gap = max(0, target_pct - compatibility_pct)
        
        return f"""### Key Result 3: Upgrade or replace 90% of Windows 11-incompatible devices by October 31, 2025 (📌)

| Category | Total | Compatible | Incompatible | Target | Current | Gap | Status |
|----------|-------|------------|--------------|--------|---------|-----|--------|
| All Devices | {metrics['total_devices']} | {metrics['compatible_device_count']} ({compatibility_pct:.1f}%) | {metrics['total_devices'] - metrics['compatible_device_count']} ({100-compatibility_pct:.1f}%) | {target_pct}% | {compatibility_pct:.1f}% | {gap:.1f}% | {status_emoji} {status_text} |

**Windows 11 Compatibility Progress:**
- {compat_progress_bar} {compatibility_pct:.1f}% Complete

**Windows 11 Adoption Progress:**
- {adoption_progress_bar} {win11_adoption_pct:.1f}% Complete

**Action Plan:**
- Address all {metrics['total_devices'] - metrics['compatible_device_count']} ESOL devices through remediation plan
- Continue migration plan for compatible Enterprise devices
- Special handling for kiosk devices to be re-provisioned to LTSC

---

"""
    
    def _format_kr4_section(self, metrics: Dict[str, Any]) -> str:
        """Format KR4 section - pure formatting"""
        enterprise_kiosks = metrics['enterprise_kiosk_count']
        status_level = metrics['kr4_status_level']
        progress_score = metrics['kr4_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        progress_bar = self._generate_progress_bar(progress_score)
        
        compliance_text = 'COMPLIANT' if enterprise_kiosks == 0 else 'NON-COMPLIANT'
        
        return f"""### Key Result 4: Re-provision Enterprise kiosk devices to LTSC by June 30, 2025 (📌)

| Requirement | Target | Current Status | Compliance | Deadline |
|-------------|--------|----------------|------------|----------|
| Enterprise Kiosk Re-provisioning | 0 devices | {enterprise_kiosks} devices | {status_emoji} {compliance_text} | June 30, 2025 |

**Implementation Progress:**
- {progress_bar} {progress_score:.0f}% Complete

**Action Plan:**
- Re-provision {enterprise_kiosks} Enterprise kiosk devices to LTSC
- Implement structured procurement limits (≤25% in Q4)
- Maintain deployable capacity ≤3 months

---

"""
    
    def _format_dashboard_section(self, metrics: Dict[str, Any]) -> str:
        """Format OKR dashboard section - pure formatting"""
        overall_score = metrics['overall_score']
        overall_status_level = metrics['overall_status_level']
        overall_status_text = self.status_text_map[overall_status_level]
        overall_status_emoji = self.status_emoji_map[overall_status_level]
        
        return f"""## OKR Success Metrics Dashboard

| Key Result | Weight | Target | Current | Progress | Weighted Score | Status |
|------------|--------|--------|---------|----------|----------------|--------|
| KR1: 2024 ESOL → 0% | {self.okr_config['okr_weights']['kr1_esol_2024']}% | 0% ESOL | {metrics['esol_2024_percentage']:.2f}% ESOL | {metrics['kr1_progress_score']:.0f}% | {metrics['kr1_weighted_score']:.1f}% | {self.status_emoji_map[metrics['kr1_status_level']]} {self.status_text_map[metrics['kr1_status_level']]} |
| KR2: 2025 ESOL → 0% | {self.okr_config['okr_weights']['kr2_esol_2025']}% | 0% ESOL | {metrics['esol_2025_percentage']:.2f}% ESOL | {metrics['kr2_progress_score']:.0f}% | {metrics['kr2_weighted_score']:.1f}% | {self.status_emoji_map[metrics['kr2_status_level']]} {self.status_text_map[metrics['kr2_status_level']]} |
| KR3: Win11 Compatibility ≥90% | {self.okr_config['okr_weights']['kr3_win11_compatibility']}% | 90% | {metrics['compatibility_percentage']:.1f}% | {metrics['kr3_progress_score']:.0f}% | {metrics['kr3_weighted_score']:.1f}% | {self.status_emoji_map[metrics['kr3_status_level']]} {self.status_text_map[metrics['kr3_status_level']]} |
| KR4: Kiosk Re-provisioning | {self.okr_config['okr_weights']['kr4_kiosk_reprovisioning']}% | 0 devices | {metrics['enterprise_kiosk_count']} devices | {metrics['kr4_progress_score']:.0f}% | {metrics['kr4_weighted_score']:.1f}% | {self.status_emoji_map[metrics['kr4_status_level']]} {self.status_text_map[metrics['kr4_status_level']]} |
| **Overall OKR Completion** | **100%** | **All Targets** | **Mixed** | **{overall_score:.1f}%** | **{overall_score:.1f}%** | **{overall_status_emoji} {overall_status_text}** |

**Current Fleet Composition:**
- Total Devices: {metrics['total_devices']:,}
- ESOL 2024: {metrics['esol_2024_count']} devices ({metrics['esol_2024_percentage']:.2f}%)
- ESOL 2025: {metrics['esol_2025_count']} devices ({metrics['esol_2025_percentage']:.2f}%)
- **Total ESOL: {metrics['total_devices'] - metrics['compatible_device_count']} devices ({100-metrics['compatibility_percentage']:.2f}%)**
- Non-ESOL: {metrics['compatible_device_count']} devices ({metrics['compatibility_percentage']:.2f}%)

---

"""
    
    def _format_risk_section(self) -> str:
        """Format risk assessment section - pure formatting"""
        return """## Risk Assessment & Mitigation

| Risk Area | Impact | Probability | Score | Mitigation Strategy |
|-----------|--------|------------|-------|---------------------|
| ESOL 2024 Timeline | High | High | 9 | Expedite procurement, dedicated resources |
| Supply Chain Delays | High | Medium | 6 | Early ordering, multiple suppliers |
| Budget Overruns | Medium | Medium | 4 | Regular forecasting, phased approach |
| Resource Constraints | Medium | High | 6 | Cross-train team, contractor support |
| User Disruption | Low | Medium | 2 | Communication plan, scheduled maintenance |

## Next Review Date
*Weekly cadence recommended*
"""
    
    def _generate_progress_bar(self, percentage: float) -> str:
        """Generate visual progress bar - pure formatting"""
        filled_blocks = int(percentage / 10)
        empty_blocks = 10 - filled_blocks
        return '🟩' * filled_blocks + '⬜' * empty_blocks
    
    def format_executive_summary(self, all_metrics: Dict[str, Any]) -> str:
        """Generate executive summary - pure formatting"""
        overall_status_emoji = self.status_emoji_map[all_metrics['overall_status_level']]
        overall_status_text = self.status_text_map[all_metrics['overall_status_level']]
        
        return f"""# Executive Summary - Technical Debt Remediation OKR

**Overall Status: {overall_status_emoji} {overall_status_text} ({all_metrics['overall_score']:.1f}%)**

## Key Highlights
- **ESOL 2024**: {all_metrics['esol_2024_count']} devices require immediate replacement
- **Windows 11 Compatibility**: {all_metrics['compatibility_percentage']:.1f}% achieved (target: 90%)
- **Total Investment Required**: Procurement needed for {all_metrics['total_devices'] - all_metrics['compatible_device_count']} devices

## Critical Actions Required
1. **Immediate**: Procure {all_metrics['esol_2024_count']} ESOL 2024 devices by June 30
2. **Q3 Focus**: Plan {all_metrics['kr2_milestone_target_devices']} ESOL 2025 device replacements
3. **Kiosk Remediation**: Re-provision {all_metrics['enterprise_kiosk_count']} Enterprise kiosk devices to LTSC

## Progress by Key Result
- **KR1 (25%)**: {self.status_emoji_map[all_metrics['kr1_status_level']]} {all_metrics['kr1_weighted_score']:.1f}% weighted
- **KR2 (25%)**: {self.status_emoji_map[all_metrics['kr2_status_level']]} {all_metrics['kr2_weighted_score']:.1f}% weighted  
- **KR3 (40%)**: {self.status_emoji_map[all_metrics['kr3_status_level']]} {all_metrics['kr3_weighted_score']:.1f}% weighted
- **KR4 (10%)**: {self.status_emoji_map[all_metrics['kr4_status_level']]} {all_metrics['kr4_weighted_score']:.1f}% weighted
"""

    def format_site_analysis(self, site_data: Dict[str, Dict[str, int]], top_n: int = 5) -> str:
        """Format site analysis - pure formatting"""
        # Sort sites by total ESOL count
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


class OKRAnalysisOrchestrator:
    """Main orchestrator that coordinates all components"""
    
    def __init__(self, config_path: str = "config/"):
        self.config = ConfigManager(config_path)
        self.data_analyzer = DataAnalyzer(self.config)
        self.business_calculator = BusinessLogicCalculator(self.config)
        self.formatter = PresentationFormatter(self.config)
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Complete analysis pipeline - orchestrates all layers"""
        # Layer 1: Pure Data Analysis
        df = self.data_analyzer.load_data(filepath)
        raw_counts = self.data_analyzer.extract_basic_counts(df)
        kiosk_counts = self.data_analyzer.extract_kiosk_counts(df)
        site_counts = self.data_analyzer.extract_site_counts(df)
        cost_totals = self.data_analyzer.extract_cost_totals(df)
        
        # Combine raw data
        all_raw_data = {**raw_counts, **kiosk_counts}
        
        # Layer 2: Pure Business Logic
        percentages = self.business_calculator.calculate_percentages(all_raw_data)
        compatibility = self.business_calculator.calculate_windows11_compatibility(all_raw_data)
        progress_scores = self.business_calculator.calculate_kr_progress_scores(
            all_raw_data, percentages, compatibility)
        weighted_scores = self.business_calculator.calculate_weighted_scores(progress_scores)
        overall_score = self.business_calculator.calculate_overall_score(weighted_scores)
        status_levels = self.business_calculator.calculate_status_levels(progress_scores)
        milestone_metrics = self.business_calculator.calculate_milestone_metrics(all_raw_data, percentages)
        
        # Combine all calculated metrics
        all_metrics = {
            **all_raw_data,
            **percentages,
            **compatibility,
            **progress_scores,
            **weighted_scores,
            **status_levels,
            **milestone_metrics,
            **cost_totals,
            'overall_score': overall_score,
            'site_data': site_counts
        }
        
        return all_metrics
    
    def generate_full_report(self, filepath: str) -> str:
        """Generate complete OKR tracking report"""
        metrics = self.analyze_file(filepath)
        return self.formatter.format_okr_tracker(metrics)
    
    def generate_executive_summary(self, filepath: str) -> str:
        """Generate executive summary"""
        metrics = self.analyze_file(filepath)
        return self.formatter.format_executive_summary(metrics)
    
    def generate_site_analysis(self, filepath: str, top_n: int = 5) -> str:
        """Generate site-level analysis"""
        metrics = self.analyze_file(filepath)
        return self.formatter.format_site_analysis(metrics['site_data'], top_n)
    
    def get_metrics_json(self, filepath: str) -> Dict[str, Any]:
        """Get raw metrics as JSON for API integration"""
        return self.analyze_file(filepath)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Analyze ESOL device data for OKR tracking')
    add_data_file_argument(parser, 'Path to the Excel file containing device data')
    parser.add_argument('--config-path', default='config/', help='Path to configuration directory')
    parser.add_argument('--output', '-o', help='Output file for the report (optional - auto-saves to data/reports/ if not specified)')
    parser.add_argument('--format', choices=['full', 'executive', 'site', 'json', 'quick'], 
                       default='full', help='Report format')
    parser.add_argument('--top-sites', type=int, default=5, 
                       help='Number of top sites to include in site analysis')
    
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator
        orchestrator = OKRAnalysisOrchestrator(args.config_path)
        
        # Generate report based on format
        data_file = get_data_file_path(args.data_file)
        validate_data_file(data_file)
        
        if args.format == 'full':
            report = orchestrator.generate_full_report(data_file)
        elif args.format == 'executive':
            report = orchestrator.generate_executive_summary(data_file)
        elif args.format == 'site':
            report = orchestrator.generate_site_analysis(data_file, args.top_sites)
        elif args.format == 'quick':
            # Quick status check
            metrics = orchestrator.get_metrics_json(data_file)
            report = f"""🎯 OKR QUICK STATUS CHECK
{'='*50}
Overall Score: {metrics['overall_score']:.1f}%
Status: {['🔴 AT RISK', '🟡 CAUTION', '🟢 ON TRACK'][metrics['overall_status_level']]}

Key Metrics:
• ESOL 2024: {metrics['esol_2024_count']} devices ({metrics['esol_2024_percentage']:.1f}%)
• ESOL 2025: {metrics['esol_2025_count']} devices ({metrics['esol_2025_percentage']:.1f}%)
• Win11 Compatibility: {metrics['compatibility_percentage']:.1f}%
• Enterprise Kiosks: {metrics['enterprise_kiosk_count']} need re-provisioning

Priority Actions:
1. 🔴 Immediate: Procure {metrics['esol_2024_count']} ESOL 2024 devices
2. 🟡 Q3 Planning: {metrics['kr2_milestone_target_devices']} ESOL 2025 devices  
3. 🟢 Re-provision: {metrics['enterprise_kiosk_count']} Enterprise kiosk devices

Total Investment: {metrics['total_devices'] - metrics['compatible_device_count']} devices requiring replacement
"""
        elif args.format == 'json':
            import json
            metrics = orchestrator.get_metrics_json(data_file)
            report = json.dumps(metrics, indent=2)
        
        # Output report
        if args.output:
            # User specified output path
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved to {output_path}")
        else:
            # Auto-save to data/reports/ with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path('data/reports')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename based on format
            if args.format == 'executive':
                filename = output_dir / f'Executive_Summary_{timestamp}.md'
            elif args.format == 'full':
                filename = output_dir / f'Full_OKR_Report_{timestamp}.md'
            elif args.format == 'site':
                filename = output_dir / f'Site_Analysis_{timestamp}.md'
            elif args.format == 'quick':
                filename = output_dir / f'Quick_Status_{timestamp}.md'
            elif args.format == 'json':
                filename = output_dir / f'OKR_Metrics_{timestamp}.json'
            else:
                filename = output_dir / f'Report_{timestamp}.md'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report auto-saved to {filename}")
            print(report)
            
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


# Example usage functions for IT Operations Director
def quick_status_check():
    """Quick status check for executive briefings"""
    orchestrator = OKRAnalysisOrchestrator()
    
    # Use the known ESOL data file
    filepath = 'data/raw/EUC_ESOL.xlsx'
    
    try:
        metrics = orchestrator.get_metrics_json(filepath)
        
        print("🎯 OKR STATUS CHECK")
        print("=" * 50)
        print(f"Overall Score: {metrics['overall_score']:.1f}%")
        print(f"ESOL 2024: {metrics['esol_2024_count']} devices (🔴 AT RISK)")
        print(f"ESOL 2025: {metrics['esol_2025_count']} devices")
        print(f"Win11 Compatibility: {metrics['compatibility_percentage']:.1f}%")
        print(f"Enterprise Kiosks: {metrics['enterprise_kiosk_count']} need re-provisioning")
        
    except FileNotFoundError:
        print("❌ Data file not found. Please ensure 'data/raw/EUC_ESOL.xlsx' exists")

def generate_weekly_update():
    """Generate weekly executive update"""
    orchestrator = OKRAnalysisOrchestrator()
    
    # Use the known ESOL data file
    filepath = 'data/raw/EUC_ESOL.xlsx'
    
    try:
        summary = orchestrator.generate_executive_summary(filepath)
        
        # Save with timestamp in reports folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        output_dir = Path('data/reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f'Technical_Debt_OKR_Update_{timestamp}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"📊 Weekly update saved to {filename}")
        
    except FileNotFoundError:
        print("❌ Data file not found. Please ensure 'data/raw/EUC_ESOL.xlsx' exists")


if __name__ == "__main__":
    main()