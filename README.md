# ESOL EUC Device Data Analysis

This project provides tools to analyze End User Computing (EUC) device data for technical debt remediation, OKR tracking, and device refresh planning. It helps summarize device status, site-level needs, and cost projections for upcoming refresh cycles.

## Project Structure

- `scripts/` — Python scripts for analysis
- `data/raw/` — Raw input data (Excel files, not tracked in git)
- `data/processed/` — Processed outputs and exports (e.g., per-site summaries, auto-generated site tables)
- `data/reports/` — Reports and executive summaries (auto-saved by all scripts)
- `config/` — YAML configuration files for OKR criteria and ESOL definitions

## Setup

1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Place your raw Excel data file (e.g., `EUC_ESOL.xlsx`) in `data/raw/`.

## Quick Start - Helper Tools

### 🎯 OKR Dashboard (Recommended)
Easy-to-use interactive dashboard for daily OKR analysis:
```sh
python scripts/okr_dashboard.py
```

### ⚡ Quick ESOL Analysis
For quick device counts and categories:
```bat
# Windows batch file
.\run_simple_analysis.bat

# Or directly with Python
python scripts/euc_count.py
```

### 🔧 Configuration Helper
Manage and validate OKR settings:
```sh
python scripts/config_helper.py
```

## Analysis Scripts

### 1. OKR Dashboard (Recommended)
**`okr_dashboard.py`** - Interactive dashboard for comprehensive OKR analysis

#### Features:
- Quick status check (daily use)
- Executive summary (management reports)
- Full OKR tracker (comprehensive analysis)
- Site analysis (priority locations)
- Save executive reports with timestamps

#### Usage:
```sh
python scripts/okr_dashboard.py
```

### 2. OKR Tracker Generator
**`okr_tracker.py`** - Professional OKR tracking with comprehensive reporting

#### Features:
- **Complete OKR framework** with weighted scoring system
- **Progress tracking** with visual indicators and status levels
- **Executive summaries** with financial impact analysis
- **Site prioritization** based on ESOL device density
- **Baseline tracking** for progress measurement over time
- **Professional markdown output** with emojis and progress bars

#### Usage Examples:
```sh
# Basic OKR report - auto-saves to data/reports/
python scripts/okr_tracker.py data/raw/EUC_ESOL.xlsx

# Custom output location
python scripts/okr_tracker.py data/raw/EUC_ESOL.xlsx --output monthly_okr_report.md

# With previous data comparison
python scripts/okr_tracker.py data/raw/EUC_ESOL.xlsx --previous-data july_metrics.json --save-metrics august_metrics.json

# Save current metrics for future comparison
python scripts/okr_tracker.py data/raw/EUC_ESOL.xlsx --save-metrics current_metrics.json
```

### 3. Simple ESOL Counter
**`euc_count.py`** - Simple device counting with category filtering and site summary table

**Features:**
- Category-based ESOL device counting (2024, 2025, 2026, all)
- Site summary table showing ESOL devices and replacement costs by location
- **Auto-exports site data to `data/processed/`** (CSV + JSON formats)
- Auto-saves reports to data/reports/ directory
- Optional custom output paths

#### Usage Examples:
```sh
# All categories (default) - auto-saves to data/reports/
python scripts/euc_count.py

# Specific categories - auto-saves to data/reports/
python scripts/euc_count.py --category esol_2024
python scripts/euc_count.py --category esol_2025
python scripts/euc_count.py --category esol_2026

# Site summary table - ESOL devices and cost by site
# Auto-exports to data/processed/ (CSV + JSON)
python scripts/euc_count.py --site-table

# Combine category and site table
python scripts/euc_count.py --category esol_2024 --site-table

# Custom output location (optional)
python scripts/euc_count.py --output "my_custom_report.md"
```

### 4. Advanced OKR Analyzer
**`separated_esol_analyzer.py`** - Comprehensive OKR tracking with clean architecture

#### Usage Examples:
```sh
# Quick status check - auto-saves to data/reports/
python scripts/separated_esol_analyzer.py --format quick

# Executive summary - auto-saves to data/reports/
python scripts/separated_esol_analyzer.py --format executive

# Full OKR tracker - auto-saves to data/reports/
python scripts/separated_esol_analyzer.py --format full

# Site analysis - auto-saves to data/reports/
python scripts/separated_esol_analyzer.py --format site --top-sites 10

# JSON export - auto-saves to data/reports/
python scripts/separated_esol_analyzer.py --format json

# Custom output location (optional)
python scripts/separated_esol_analyzer.py --format executive --output "special_report.md"
```

### 5. ESOL Data Analysis
**`esol-data-analysis-python.py`** - Comprehensive ESOL analysis with cost projections

#### Usage Examples:
```sh
# Full analysis - auto-saves to data/reports/
python scripts/esol-data-analysis-python.py

# JSON metrics - auto-saves to data/reports/
python scripts/esol-data-analysis-python.py --json

# Custom output location (optional)
python scripts/esol-data-analysis-python.py --output "cost_analysis.md"
```

## 📁 Auto-Save Reports

**All scripts now automatically save reports to `data/reports/` when no output path is specified:**

- **Timestamped files**: No more overwriting previous reports
- **Format-specific naming**: Each script generates appropriately named files
- **Consistent behavior**: Same auto-save pattern across all analysis scripts
- **Optional custom paths**: Still supports `--output` parameter for custom locations

### Report File Naming:
- `OKR_Tracker_{timestamp}.md` - from `okr_tracker.py` (auto-saves to data/reports/)
- `ESOL_Count_{category}_{timestamp}.md` - from `euc_count.py`
- `Executive_Summary_{timestamp}.md` - from `separated_esol_analyzer.py`
- `Quick_Status_{timestamp}.md` - from `separated_esol_analyzer.py`
- `ESOL_Analysis_{timestamp}.md` - from `esol-data-analysis-python.py`
- `OKR_Metrics_{timestamp}.json` - from `separated_esol_analyzer.py`

## 🎯 OKR Tracking Features

### **Professional OKR Framework**
The `okr_tracker.py` script provides enterprise-grade OKR tracking:

- **Weighted Scoring System**: KR1 (25%), KR2 (25%), KR3 (40%), KR4 (10%)
- **Progress Visualization**: Progress bars, status emojis, and color-coded indicators
- **Baseline Tracking**: Historical progress measurement with configurable baselines
- **Financial Impact**: Cost projections and replacement budget planning
- **Site Prioritization**: Top 5 sites ranked by ESOL device density
- **Executive Reporting**: Management-ready summaries with actionable recommendations

### **Key Results Tracked**
1. **KR1**: ESOL 2024 remediation (0% target by June 30, 2025)
2. **KR2**: ESOL 2025 remediation (50% milestone by June 30, 100% by Dec 31, 2025)
3. **KR3**: Windows 11 compatibility (90% target by October 31, 2025)
4. **KR4**: Enterprise kiosk LTSC re-provisioning (0 devices by June 30, 2025)

## 📊 Processed Data Exports

**Site analysis data automatically exported to `data/processed/` for further analysis:**

### Site Summary Exports:
- **CSV Format**: `site_esol_summary_{timestamp}.csv` - Excel/Sheets compatible
- **JSON Format**: `site_esol_summary_{timestamp}.json` - API/programmatic use
- **Data Includes**: ESOL counts by year (2024, 2025, 2026), total devices, replacement costs
- **Auto-generated**: Created automatically when using `--site-table` option

### Export Location:
```
data/processed/
├── site_esol_summary_20250815_112356.csv  ← CSV format
└── site_esol_summary_20250815_112356.json ← JSON format
```

## Batch Files (Windows)

### `run_dashboard.bat`
Launches the interactive OKR dashboard:
```cmd
.\run_dashboard.bat
```

### `run_okr_tracker.bat` (NEW)
Professional OKR tracking with comprehensive reporting:
```cmd
# Show help
.\run_okr_tracker.bat help

# Basic OKR report (auto-saves to data/reports/)
.\run_okr_tracker.bat

# Monthly report with timestamped filename
.\run_okr_tracker.bat monthly

# Compare with previous metrics
.\run_okr_tracker.bat compare july_metrics.json

# Save current metrics for future comparison
.\run_okr_tracker.bat metrics
```

### `run_simple_analysis.bat`
Quick ESOL analysis with category filtering:
```cmd
# Show help
.\run_simple_analysis.bat help

# All categories
.\run_simple_analysis.bat

# Specific category
.\run_simple_analysis.bat esol_2024
.\run_simple_analysis.bat esol_2025
.\run_simple_analysis.bat esol_2026
```

## Current Data Summary

Based on your latest OKR tracker analysis:
- **Total Devices**: 4,348
- **ESOL 2024**: 55 devices (1.26%) - 🔴 AT RISK
- **ESOL 2025**: 339 devices (7.80%) - 🔴 AT RISK
- **Total ESOL**: 757 devices (17.41%) - includes ESOL 2026
- **Windows 11 Compatibility**: 82.6% - 🟡 CAUTION (target: 90%)
- **Windows 11 Adoption**: 69.2% - 🟡 CAUTION
- **Enterprise Kiosks**: 159 need LTSC re-provisioning - 🔴 AT RISK
- **Overall OKR Completion**: 43.2% - 🔴 AT RISK

## Top Priority Sites
1. **Izmir**: 211 ESOL devices (38 ESOL 2024, 102 ESOL 2025)
2. **Blois**: 171 ESOL devices (1 ESOL 2024, 66 ESOL 2025)
3. **Iasi**: 142 ESOL devices (0 ESOL 2024, 41 ESOL 2025)

## Requirements

- Python 3.8+
- pandas
- openpyxl
- pyyaml

Install with:
```sh
pip install -r requirements.txt
```