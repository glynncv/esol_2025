#!/usr/bin/env python3
"""
Technical Debt Remediation OKR Tracker Generator
Analyzes EUC_ESOL.xlsx and generates comprehensive OKR markdown report

Requirements:
    pip install pandas openpyxl
    
Usage:
    python okr_tracker.py EUC_ESOL.xlsx [--output okr_report.md] [--previous-data previous_metrics.json]
"""

import pandas as pd
import json
import argparse
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from data_utils import get_data_file_path, add_data_file_argument, validate_data_file


class ESOLDataAnalyzer:
    """Analyzes ESOL data and calculates OKR metrics"""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data = None
        self.total_devices = 0
        
    def load_data(self) -> pd.DataFrame:
        """Load Excel data and standardize column names"""
        try:
            # Try multiple sheet names
            excel_file = pd.ExcelFile(self.filepath)
            sheet_name = excel_file.sheet_names[0]  # Use first sheet
            
            self.data = pd.read_excel(self.filepath, sheet_name=sheet_name)
            self.total_devices = len(self.data)
            
            # Standardize column names (handle variations)
            column_mapping = {
                'Action to take': 'action',
                'OS Build': 'os_build', 
                'Current OS Build': 'os_build',
                'Enterprise or LTSC': 'edition',
                'LTSC or Enterprise': 'edition',
                'Current User LoggedOn': 'current_user',
                'Current User Logged On': 'current_user',
                'Last User LoggedOn': 'last_user',
                'Last User Logged On': 'last_user',
                'Site Location': 'site',
                'Site Location AD': 'site',
                'Cost for Replacement $': 'cost',
                'Device Name': 'device_name'
            }
            
            # Rename columns to standard names
            for original, standard in column_mapping.items():
                if original in self.data.columns:
                    self.data = self.data.rename(columns={original: standard})
            
            print(f"Successfully loaded {self.total_devices:,} devices")
            print(f"Columns available: {list(self.data.columns)}")
            
            return self.data
            
        except Exception as e:
            raise RuntimeError(f"Failed to load data from {self.filepath}: {e}")
    
    def analyze_esol_categories(self) -> Dict[str, Any]:
        """Analyze ESOL device categories"""
        if self.data is None:
            self.load_data()
        
        # Count action categories
        action_counts = self.data['action'].value_counts().to_dict()
        
        # ESOL category mapping
        esol_2024 = action_counts.get('Urgent Replacement', 0)
        esol_2025 = action_counts.get('Replace by 14/10/2025', 0)
        esol_2026 = action_counts.get('Replace by 11/11/2026', 0)
        redeploy = action_counts.get('Redeploy', 0)
        na_count = action_counts.get('N/A', 0)
        
        total_esol = esol_2024 + esol_2025 + esol_2026
        
        return {
            'esol_2024_count': esol_2024,
            'esol_2025_count': esol_2025,
            'esol_2026_count': esol_2026,
            'redeploy_count': redeploy,
            'na_count': na_count,
            'total_esol_count': total_esol,
            'esol_2024_percentage': (esol_2024 / self.total_devices) * 100,
            'esol_2025_percentage': (esol_2025 / self.total_devices) * 100,
            'total_esol_percentage': (total_esol / self.total_devices) * 100,
            'action_distribution': action_counts
        }
    
    def analyze_windows11_status(self) -> Dict[str, Any]:
        """Analyze Windows 11 compatibility and adoption for Enterprise devices only"""
        if self.data is None:
            self.load_data()
        
        # Filter for Enterprise devices only (the 2025 Windows 11 push target)
        enterprise_mask = self.data['edition'] == 'Enterprise'
        enterprise_df = self.data[enterprise_mask]
        
        # Count Enterprise devices already on Windows 11
        win11_mask = enterprise_df['os_build'].str.contains('Win11', na=False)
        enterprise_win11_count = win11_mask.sum()
        
        # Count Enterprise devices that will get Windows 11 via ESOL replacement
        esol_data = self.analyze_esol_categories()
        enterprise_esol_mask = enterprise_df['action'].isin(['Urgent Replacement', 'Replace by 14/10/2025'])
        enterprise_esol_count = enterprise_esol_mask.sum()
        
        # Calculate Enterprise Windows 11 adoption path
        total_enterprise = len(enterprise_df)
        total_enterprise_win11_path = enterprise_win11_count + enterprise_esol_count
        enterprise_win11_adoption_pct = (total_enterprise_win11_path / total_enterprise) * 100 if total_enterprise > 0 else 0
        current_win11_pct = (enterprise_win11_count / total_enterprise) * 100 if total_enterprise > 0 else 0
        
        # Count by edition (for reference)
        enterprise_count = (self.data['edition'] == 'Enterprise').sum()
        ltsc_count = (self.data['edition'] == 'LTSC').sum()
        
        return {
            'win11_count': enterprise_win11_count,
            'win11_adoption_percentage': current_win11_pct,
            'enterprise_win11_adoption_percentage': enterprise_win11_adoption_pct,
            'enterprise_win11_path_count': total_enterprise_win11_path,
            'enterprise_esol_count': enterprise_esol_count,
            'enterprise_count': enterprise_count,
            'ltsc_count': ltsc_count,
            'compatible_devices': total_enterprise_win11_path,  # Enterprise devices on Win11 path
            'compatibility_percentage': enterprise_win11_adoption_pct,
            'enterprise_percentage': (enterprise_count / self.total_devices) * 100
        }
    
    def analyze_kiosk_devices(self) -> Dict[str, Any]:
        """Analyze kiosk devices (GID/kiosk accounts)"""
        if self.data is None:
            self.load_data()
        
        # Check for kiosk patterns in user fields
        current_user_kiosk = self.data['current_user'].str.contains('gid|kiosk', case=False, na=False)
        last_user_kiosk = self.data['last_user'].str.contains('gid|kiosk', case=False, na=False)
        
        # Combine conditions (OR logic)
        kiosk_mask = current_user_kiosk | last_user_kiosk
        kiosk_devices = self.data[kiosk_mask]
        
        # Count Enterprise kiosks
        enterprise_kiosks = kiosk_devices[kiosk_devices['edition'] == 'Enterprise'].shape[0]
        ltsc_kiosks = kiosk_devices[kiosk_devices['edition'] == 'LTSC'].shape[0]
        
        return {
            'total_kiosk_count': len(kiosk_devices),
            'enterprise_kiosk_count': enterprise_kiosks,
            'ltsc_kiosk_count': ltsc_kiosks,
            'kiosk_percentage': (len(kiosk_devices) / self.total_devices) * 100
        }
    
    def analyze_by_site(self) -> Dict[str, Dict[str, int]]:
        """Analyze ESOL devices by site location"""
        if self.data is None:
            self.load_data()
        
        # Filter ESOL devices
        esol_2024_mask = self.data['action'] == 'Urgent Replacement'
        esol_2025_mask = self.data['action'] == 'Replace by 14/10/2025'
        
        # Group by site
        esol_2024_by_site = self.data[esol_2024_mask]['site'].value_counts().to_dict()
        esol_2025_by_site = self.data[esol_2025_mask]['site'].value_counts().to_dict()
        
        # Combine site data
        all_sites = set(list(esol_2024_by_site.keys()) + list(esol_2025_by_site.keys()))
        
        site_analysis = {}
        for site in all_sites:
            if pd.isna(site):
                continue
            esol_2024_count = esol_2024_by_site.get(site, 0)
            esol_2025_count = esol_2025_by_site.get(site, 0)
            total_esol = esol_2024_count + esol_2025_count
            
            site_analysis[site] = {
                'esol_2024': esol_2024_count,
                'esol_2025': esol_2025_count,
                'total_esol': total_esol
            }
        
        # Sort by total ESOL devices
        return dict(sorted(site_analysis.items(), 
                          key=lambda x: x[1]['total_esol'], 
                          reverse=True))
    
    def calculate_replacement_costs(self) -> Dict[str, float]:
        """Calculate replacement costs (if cost column available)"""
        if self.data is None:
            self.load_data()
        
        if 'cost' not in self.data.columns:
            # Use default cost estimate
            default_cost = 1600
            esol_data = self.analyze_esol_categories()
            return {
                'esol_2024_cost': esol_data['esol_2024_count'] * default_cost,
                'esol_2025_cost': esol_data['esol_2025_count'] * default_cost,
                'total_replacement_cost': esol_data['total_esol_count'] * default_cost
            }
        
        # Calculate from actual cost data
        esol_2024_mask = self.data['action'] == 'Urgent Replacement'
        esol_2025_mask = self.data['action'] == 'Replace by 14/10/2025'
        
        esol_2024_cost = self.data[esol_2024_mask]['cost'].fillna(1600).sum()
        esol_2025_cost = self.data[esol_2025_mask]['cost'].fillna(1600).sum()
        
        return {
            'esol_2024_cost': float(esol_2024_cost),
            'esol_2025_cost': float(esol_2025_cost),
            'total_replacement_cost': float(esol_2024_cost + esol_2025_cost)
        }


class OKRCalculator:
    """Calculates OKR metrics and progress scores"""
    
    def __init__(self, analyzer: ESOLDataAnalyzer):
        self.analyzer = analyzer
        # Baseline constants for progress calculations
        self.BASELINE_ESOL_2024 = 60
        self.BASELINE_ESOL_2025 = 400
        self.BASELINE_ENTERPRISE_KIOSKS = 170
        
        self.weights = {
            'kr1_esol_2024': 25,
            'kr2_esol_2025': 25,
            'kr3_win11_compatibility': 40,
            'kr4_kiosk_reprovisioning': 10
        }
        self.targets = {
            'kr1_target_percentage': 0,
            'kr2_target_percentage': 0,
            'kr2_milestone_percentage': 50,
            'kr3_target_percentage': 90,
            'kr4_target_count': 0
        }
    
    def calculate_kr_metrics(self) -> Dict[str, Any]:
        """Calculate all OKR metrics"""
        esol_data = self.analyzer.analyze_esol_categories()
        win11_data = self.analyzer.analyze_windows11_status()
        kiosk_data = self.analyzer.analyze_kiosk_devices()
        cost_data = self.analyzer.calculate_replacement_costs()
        site_data = self.analyzer.analyze_by_site()
        
        # KR1: ESOL 2024 progress
        kr1_progress = 100.0 if esol_data['esol_2024_percentage'] <= self.targets['kr1_target_percentage'] else 0.0
        if esol_data['esol_2024_count'] > 0:
            # Estimate progress based on previous baseline (if available)
            kr1_progress = max(0, 100 - (esol_data['esol_2024_count'] / self.BASELINE_ESOL_2024 * 100))
        
        # KR2: ESOL 2025 progress
        kr2_progress = 100.0 if esol_data['esol_2025_percentage'] <= self.targets['kr2_target_percentage'] else 0.0
        if esol_data['esol_2025_count'] > 0:
            # Estimate progress based on previous baseline
            kr2_progress = max(0, 100 - (esol_data['esol_2025_count'] / self.BASELINE_ESOL_2025 * 100))
        
        # KR3: Windows 11 compatibility
        kr3_current = win11_data['compatibility_percentage']
        kr3_progress = min(100.0, (kr3_current / self.targets['kr3_target_percentage']) * 100)
        
        # KR4: Kiosk re-provisioning
        kr4_progress = 100.0 if kiosk_data['enterprise_kiosk_count'] <= self.targets['kr4_target_count'] else 0.0
        if kiosk_data['enterprise_kiosk_count'] > 0:
            kr4_progress = max(0, 100 - (kiosk_data['enterprise_kiosk_count'] / self.BASELINE_ENTERPRISE_KIOSKS * 100))
        
        # Calculate weighted scores
        weighted_scores = {
            'kr1_weighted_score': kr1_progress * (self.weights['kr1_esol_2024'] / 100),
            'kr2_weighted_score': kr2_progress * (self.weights['kr2_esol_2025'] / 100),
            'kr3_weighted_score': kr3_progress * (self.weights['kr3_win11_compatibility'] / 100),
            'kr4_weighted_score': kr4_progress * (self.weights['kr4_kiosk_reprovisioning'] / 100)
        }
        
        overall_score = sum(weighted_scores.values())
        
        # Status levels
        def get_status_level(score):
            if score >= 80:
                return 2  # on_track
            elif score >= 60:
                return 1  # caution
            else:
                return 0  # at_risk
        
        return {
            'total_devices': self.analyzer.total_devices,
            **esol_data,
            **win11_data,
            **kiosk_data,
            **cost_data,
            'site_data': site_data,
            'kr1_progress_score': kr1_progress,
            'kr2_progress_score': kr2_progress,
            'kr3_progress_score': kr3_progress,
            'kr4_progress_score': kr4_progress,
            **weighted_scores,
            'overall_score': overall_score,
            'kr1_status_level': get_status_level(kr1_progress),
            'kr2_status_level': get_status_level(kr2_progress),
            'kr3_status_level': get_status_level(kr3_progress),
            'kr4_status_level': get_status_level(kr4_progress),
            'overall_status_level': get_status_level(overall_score),
            'kr2_milestone_target_devices': int(esol_data['esol_2025_count'] * 0.5)
        }


class OKRReportGenerator:
    """Generates formatted OKR tracker markdown report"""
    
    def __init__(self, metrics: Dict[str, Any], previous_metrics: Optional[Dict[str, Any]] = None):
        self.metrics = metrics
        self.previous_metrics = previous_metrics or {}
        
        # Status mappings
        self.status_text_map = {0: 'AT RISK', 1: 'CAUTION', 2: 'ON TRACK'}
        self.status_emoji_map = {0: 'AT RISK', 1: 'CAUTION', 2: 'ON TRACK'}
    
    def generate_progress_bar(self, percentage: float) -> str:
        """Generate visual progress bar"""
        filled_blocks = int(percentage / 10)
        empty_blocks = 10 - filled_blocks
        return '🟩' * filled_blocks + '⬜' * empty_blocks
    
    def calculate_changes(self) -> Dict[str, Any]:
        """Calculate changes from previous report"""
        if not self.previous_metrics:
            return {}
        
        return {
            'total_devices': self.metrics['total_devices'] - self.previous_metrics.get('total_devices', 0),
            'esol_2024': self.previous_metrics.get('esol_2024_count', 0) - self.metrics['esol_2024_count'],
            'esol_2025': self.previous_metrics.get('esol_2025_count', 0) - self.metrics['esol_2025_count'],
            'enterprise_kiosks': self.previous_metrics.get('enterprise_kiosk_count', 0) - self.metrics['enterprise_kiosk_count']
        }
    
    def generate_kr1_section(self) -> str:
        """Generate KR1 section"""
        current_pct = self.metrics['esol_2024_percentage']
        device_count = self.metrics['esol_2024_count']
        status_level = self.metrics['kr1_status_level']
        progress_score = self.metrics['kr1_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        progress_bar = self.generate_progress_bar(progress_score)
        
        return f"""### Key Result 1: Remediate 100% of 2024 ESOL equipment by June 30, 2025

| Metric | Target | Current | Gap | Deadline | Status |
|--------|--------|---------|-----|----------|--------|
| 2024 ESOL Percentage | 0% (0 devices) | {current_pct:.2f}% ({device_count} devices) | {device_count} devices | June 30, 2025 | {status_emoji} {status_text} |

**Current ESOL 2024 Percentage:**
- AT RISK: {current_pct:.2f}% (Target: 0%)

**Remediation Progress:**
- {progress_bar} {progress_score:.0f}% Complete

**Action Plan:**
- Immediate procurement for all {device_count} devices
- Establish site coordinators at all impacted locations
- Weekly status reviews until completion

---
"""
    
    def generate_kr2_section(self) -> str:
        """Generate KR2 section"""
        current_pct = self.metrics['esol_2025_percentage']
        device_count = self.metrics['esol_2025_count']
        milestone_target = self.metrics['kr2_milestone_target_devices']
        status_level = self.metrics['kr2_status_level']
        progress_score = self.metrics['kr2_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        progress_bar = self.generate_progress_bar(progress_score)
        
        return f"""### Key Result 2: Complete 50% of 2025 ESOL remediation by June 30 and 100% by December 31, 2025

| Milestone | Target | Current | Gap | Deadline | Status |
|-----------|--------|---------|-----|----------|--------|
| 50% Milestone | {milestone_target} devices remediated | {device_count} devices remaining | {milestone_target} devices | June 30, 2025 | {status_emoji} {status_text} |
| 100% Completion | 0% (0 devices) | {current_pct:.2f}% ({device_count} devices) | {device_count} devices | December 31, 2025 | {status_emoji} {status_text} |

**Current ESOL 2025 Percentage:**
- AT RISK: {current_pct:.2f}% (Target: 0% by Dec 31)

**Total Progress:**
- {progress_bar} {progress_score:.0f}% Complete

**Action Plan:**
- Accelerate Q3/Q4 procurement for {device_count} devices
- Focus on high-density sites for maximum impact
- Monthly milestone tracking with executive reviews

---
"""
    
    def generate_kr3_section(self) -> str:
        """Generate KR3 section"""
        compatibility_pct = self.metrics['compatibility_percentage']
        win11_adoption_pct = self.metrics['win11_adoption_percentage']
        status_level = self.metrics['kr3_status_level']
        progress_score = self.metrics['kr3_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        
        return f"""### Key Result 3: Upgrade or replace 90% of Windows 11-incompatible devices by October 31, 2025

| Category | Total | Compatible | Target | Current | Status |
|----------|-------|------------|--------|---------|--------|
| All Devices | {self.metrics['total_devices']:,} | {self.metrics['compatible_devices']:,} | 90% | {compatibility_pct:.1f}% | {status_emoji} {status_text} |

**Windows 11 Compatibility Progress:**
- {self.generate_progress_bar(progress_score)} {compatibility_pct:.1f}% Complete

**Windows 11 Adoption Progress:**
- {self.generate_progress_bar(win11_adoption_pct)} {win11_adoption_pct:.1f}% Complete

**Action Plan:**
- Address remaining ESOL devices through remediation plan
- Continue Windows 11 migration for compatible devices
- Maintain compatibility above target threshold

---
"""
    
    def generate_kr4_section(self) -> str:
        """Generate KR4 section"""
        enterprise_kiosks = self.metrics['enterprise_kiosk_count']
        status_level = self.metrics['kr4_status_level']
        progress_score = self.metrics['kr4_progress_score']
        
        status_text = self.status_text_map[status_level]
        status_emoji = self.status_emoji_map[status_level]
        progress_bar = self.generate_progress_bar(progress_score)
        
        return f"""### Key Result 4: Re-provision Enterprise kiosk devices to LTSC by June 30, 2025

| Requirement | Target | Current Status | Compliance | Status |
|-------------|--------|----------------|------------|---------|
| Enterprise Kiosk Re-provisioning | 0 devices | {enterprise_kiosks} devices | {status_emoji} {'COMPLIANT' if enterprise_kiosks == 0 else 'NON-COMPLIANT'} | {status_emoji} {status_text} |

**Implementation Progress:**
- {progress_bar} {progress_score:.0f}% Complete

**Action Plan:**
- Re-provision {enterprise_kiosks} Enterprise kiosk devices to LTSC
- Implement structured procurement limits
- Maintain deployable capacity guidelines

---
"""
    
    def generate_dashboard_section(self) -> str:
        """Generate OKR dashboard section"""
        overall_score = self.metrics['overall_score']
        overall_status = self.status_emoji_map[self.metrics['overall_status_level']]
        overall_text = self.status_text_map[self.metrics['overall_status_level']]
        
        return f"""## OKR Success Metrics Dashboard

| Key Result | Weight | Target | Current | Progress | Weighted Score | Status |
|------------|--------|--------|---------|----------|----------------|--------|
| KR1: 2024 ESOL → 0% | 25% | 0% ESOL | {self.metrics['esol_2024_percentage']:.2f}% ESOL | {self.metrics['kr1_progress_score']:.0f}% | {self.metrics['kr1_weighted_score']:.1f}% | {self.status_emoji_map[self.metrics['kr1_status_level']]} {self.status_text_map[self.metrics['kr1_status_level']]} |
| KR2: 2025 ESOL → 0% | 25% | 0% ESOL | {self.metrics['esol_2025_percentage']:.2f}% ESOL | {self.metrics['kr2_progress_score']:.0f}% | {self.metrics['kr2_weighted_score']:.1f}% | {self.status_emoji_map[self.metrics['kr2_status_level']]} {self.status_text_map[self.metrics['kr2_status_level']]} |
| KR3: Win11 Compatibility >=90% | 40% | 90% | {self.metrics['compatibility_percentage']:.1f}% | {self.metrics['kr3_progress_score']:.0f}% | {self.metrics['kr3_weighted_score']:.1f}% | {self.status_emoji_map[self.metrics['kr3_status_level']]} {self.status_text_map[self.metrics['kr3_status_level']]} |
| KR4: Kiosk Re-provisioning | 10% | 0 devices | {self.metrics['enterprise_kiosk_count']} devices | {self.metrics['kr4_progress_score']:.0f}% | {self.metrics['kr4_weighted_score']:.1f}% | {self.status_emoji_map[self.metrics['kr4_status_level']]} {self.status_text_map[self.metrics['kr4_status_level']]} |
| **Overall OKR Completion** | **100%** | **All Targets** | **Mixed** | **{overall_score:.1f}%** | **{overall_score:.1f}%** | **{overall_status} {overall_text}** |

**Current Fleet Composition:**
- **Total Devices**: {self.metrics['total_devices']:,}
- **ESOL 2024**: {self.metrics['esol_2024_count']} devices ({self.metrics['esol_2024_percentage']:.2f}%)
- **ESOL 2025**: {self.metrics['esol_2025_count']} devices ({self.metrics['esol_2025_percentage']:.2f}%)
- **Total ESOL**: {self.metrics['total_esol_count']} devices ({self.metrics['total_esol_percentage']:.2f}%)
- **Windows 11 Compatible**: {self.metrics['compatible_devices']} devices ({self.metrics['compatibility_percentage']:.1f}%)
- **Windows 11 Adopted**: {self.metrics['win11_count']} devices ({self.metrics['win11_adoption_percentage']:.1f}%)
- **Enterprise Kiosks Pending**: {self.metrics['enterprise_kiosk_count']} devices

---
"""
    
    def generate_site_analysis_section(self) -> str:
        """Generate top sites analysis"""
        site_data = self.metrics['site_data']
        top_sites = list(site_data.items())[:5]
        
        section = """## Top 5 Sites Requiring ESOL Remediation

"""
        for i, (site, counts) in enumerate(top_sites, 1):
            priority = "CRITICAL" if counts['esol_2024'] > 10 else "HIGH" if counts['total_esol'] > 20 else "MEDIUM"
            section += f"{i}. **{site}**: {counts['total_esol']} total ({counts['esol_2024']} ESOL 2024, {counts['esol_2025']} ESOL 2025) - {priority}\n"
        
        return section + "\n---\n\n"
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary"""
        changes = self.calculate_changes()
        
        summary = f"""## Executive Summary

### **Current OKR Status: {self.metrics['overall_score']:.1f}% Complete**

"""
        
        if changes:
            summary += f"""**Progress Since Last Report:**
- Total Devices: {self.metrics['total_devices']:,} ({changes['total_devices']:+d})
- ESOL 2024: {changes['esol_2024']:+d} devices remediated
- ESOL 2025: {changes['esol_2025']:+d} devices remediated
- Enterprise Kiosks: {changes['enterprise_kiosks']:+d} devices addressed

"""
        
        summary += f"""**Key Metrics:**
- **ESOL 2024**: {self.metrics['esol_2024_count']} devices ({self.metrics['esol_2024_percentage']:.2f}%) remaining
- **ESOL 2025**: {self.metrics['esol_2025_count']} devices ({self.metrics['esol_2025_percentage']:.2f}%) remaining  
- **Windows 11 Compatibility**: {self.metrics['compatibility_percentage']:.1f}% (target: 90%)
- **Enterprise Kiosks**: {self.metrics['enterprise_kiosk_count']} devices pending LTSC re-provisioning

**Financial Impact:**
- **Total Replacement Cost**: ${self.metrics['total_replacement_cost']:,.0f}
- **ESOL 2024 Cost**: ${self.metrics['esol_2024_cost']:,.0f}
- **ESOL 2025 Cost**: ${self.metrics['esol_2025_cost']:,.0f}

**Recommendations:**
1. Accelerate ESOL 2024 remediation with emergency procurement
2. Maintain Windows 11 compatibility excellence above 90%
3. Complete Enterprise kiosk LTSC re-provisioning program
4. Continue systematic ESOL 2025 device replacement through Q4

"""
        return summary
    
    def generate_full_report(self) -> str:
        """Generate complete OKR tracker report"""
        today = datetime.now().strftime('%B %d, %Y')
        
        report = f"""# Technical Debt Remediation OKR Tracker
*Date of Review: {today}*

## Objective: Eliminate high-risk technical debt to reduce operational cost and improve security posture.

{self.generate_kr1_section()}
{self.generate_kr2_section()}
{self.generate_kr3_section()}
{self.generate_kr4_section()}
{self.generate_dashboard_section()}
{self.generate_site_analysis_section()}
{self.generate_executive_summary()}
## Next Review Date
**{(datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')}** - Weekly cadence recommended
"""
        return report


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Generate Technical Debt Remediation OKR Tracker')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--output', '-o', 
                       help='Output markdown file (auto-saves to data/reports/ if not specified)')
    parser.add_argument('--previous-data', '-p', 
                       help='Path to JSON file with previous metrics for comparison')
    parser.add_argument('--save-metrics', '-s', 
                       help='Save current metrics to JSON file for future comparison')
    
    args = parser.parse_args()
    
    try:
        print("Starting OKR Tracker generation...")
        
        # Load previous metrics if provided
        previous_metrics = None
        if args.previous_data and Path(args.previous_data).exists():
            with open(args.previous_data, 'r') as f:
                previous_metrics = json.load(f)
                print(f"Loaded previous metrics from {args.previous_data}")
        
        # Analyze current data
        data_file = get_data_file_path(args.data_file)
        validate_data_file(data_file)
        print(f"Loading data from {data_file}")
        analyzer = ESOLDataAnalyzer(data_file)
        try:
            analyzer.load_data()
        except RuntimeError as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        print("Calculating OKR metrics...")
        calculator = OKRCalculator(analyzer)
        metrics = calculator.calculate_kr_metrics()
        
        # Generate report
        print("Generating OKR tracker report...")
        generator = OKRReportGenerator(metrics, previous_metrics)
        report = generator.generate_full_report()
        
        # Save report
        if args.output:
            # User specified output path
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {output_path}")
        else:
            # Auto-save to data/reports/ with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path('data/reports')
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = output_dir / f'OKR_Tracker_{timestamp}.md'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report auto-saved to {filename}")
        
        # Save current metrics if requested
        if args.save_metrics:
            with open(args.save_metrics, 'w') as f:
                # Remove non-serializable data
                metrics_to_save = {k: v for k, v in metrics.items() if k != 'site_data'}
                json.dump(metrics_to_save, f, indent=2)
            print(f"💾 Current metrics saved to {args.save_metrics}")
        
        # Print summary
        print("\nOKR SUMMARY:")
        print(f"Overall Completion: {metrics['overall_score']:.1f}%")
        print(f"ESOL 2024: {metrics['esol_2024_count']} devices ({metrics['esol_2024_percentage']:.2f}%)")
        print(f"ESOL 2025: {metrics['esol_2025_count']} devices ({metrics['esol_2025_percentage']:.2f}%)")
        print(f"Win11 Compatibility: {metrics['compatibility_percentage']:.1f}%")
        print(f"Enterprise Kiosks: {metrics['enterprise_kiosk_count']} devices")
        
    except KeyboardInterrupt:
        print("\n⏹️  Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# Example usage:
"""
# Basic usage
python okr_tracker.py EUC_ESOL.xlsx

# With output file specification
python okr_tracker.py EUC_ESOL.xlsx --output monthly_okr_report.md

# With previous data comparison
python okr_tracker.py EUC_ESOL.xlsx --previous-data july_metrics.json --save-metrics august_metrics.json

# Command line example with all options
python okr_tracker.py EUC_ESOL.xlsx \
    --output "Technical_Debt_OKR_$(date +%Y%m%d).md" \
    --previous-data previous_metrics.json \
    --save-metrics current_metrics.json
"""