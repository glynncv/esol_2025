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
python scripts/esol_count.py
```

### 🖥️ Kiosk EUC Analysis
For Kiosk device analysis and Windows 11 migration status:
```bat
# Windows batch file
.\run_kiosk_analysis.bat

# Or directly with Python
python scripts/kiosk_count.py
```

### 💻 Windows 11 EUC Analysis
For Windows 11 device counting:
```bat
# Windows batch file
.\run_win11_analysis.bat

# Or directly with Python
python scripts/win11_count.py
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
# Basic OKR report - auto-saves to data/reports/ (auto-detects data file)
python scripts/okr_tracker.py

# With explicit data file path
python scripts/okr_tracker.py data/raw/EUC_ESOL.xlsx

# Custom output location
python scripts/okr_tracker.py --output monthly_okr_report.md

# With previous data comparison
python scripts/okr_tracker.py --previous-data july_metrics.json --save-metrics august_metrics.json

# Save current metrics for future comparison
python scripts/okr_tracker.py --save-metrics current_metrics.json
```

### 3. Simple ESOL Counter
**`esol_count.py`** - Simple device counting with category filtering and site summary table

**Features:**
- Category-based ESOL device counting (2024, 2025, 2026, all)
- Site summary table showing ESOL devices and replacement costs by location
- **Auto-exports site data to `data/processed/`** (CSV + JSON formats)
- Auto-saves reports to data/reports/ directory
- Optional custom output paths

#### Usage Examples:
```sh
# All categories (default) - auto-saves to data/reports/
python scripts/esol_count.py

# Specific categories - auto-saves to data/reports/
python scripts/esol_count.py --category esol_2024
python scripts/esol_count.py --category esol_2025
python scripts/esol_count.py --category esol_2026

# Site summary table - ESOL devices and cost by site
# Auto-exports to data/processed/ (CSV + JSON)
python scripts/esol_count.py --site-table

# Combine category and site table
python scripts/esol_count.py --category esol_2024 --site-table

# Custom output location (optional)
python scripts/esol_count.py --output "my_custom_report.md"
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

### 5. Kiosk EUC Analysis
**`kiosk_count.py`** - Analyze Kiosk EUC counts and Windows 11 migration status

#### Features:
- **Kiosk detection** using configurable patterns (Device Name contains "SHP" OR Current User LoggedOn contains "Kiosk")
- **Enterprise vs LTSC breakdown** with percentages
- **Windows 11 migration analysis** for LTSC Kiosk machines
- **YAML configuration** integration for flexible pattern matching
- **Auto-saves reports** to data/reports/ directory

#### Usage Examples:
```sh
# Basic kiosk analysis - auto-saves to data/reports/
python scripts/kiosk_count.py

# Custom output location (optional)
python scripts/kiosk_count.py --output "kiosk_analysis.md"
```

### 6. Windows 11 EUC Analysis
**`win11_count.py`** - Analyze Windows 11 adoption for Enterprise EUCs (2025 push strategy)

#### Features:
- **Enterprise-focused analysis** - Only counts Enterprise EUCs (the 2025 Windows 11 push target)
- **Migration pathway tracking** - Shows current Win11 + ESOL replacement pathway
- **LTSC exclusion** - LTSC devices excluded from Windows 11 push strategy
- **Auto-saves reports** to data/reports/ directory

### 7. EUC Summary Validation
**`euc_summary.py`** - Cross-tool validation script for EUC device inventory metrics

#### Features:
- **Standardized metrics extraction** - Core EUC metrics for validation
- **Cross-tool compatibility** - Consistent output format for comparison
- **Multiple output formats** - Text and JSON formats supported
- **Data integrity validation** - Hash fingerprinting and key metric sums
- **Enterprise-focused Windows 11 calculations** - Aligned with 2025 strategy
- **Smart file detection** - Auto-detects data files with override capability

#### Usage Examples:
```sh
# Basic Windows 11 analysis - auto-saves to data/reports/
python scripts/win11_count.py

# Custom output location (optional)
python scripts/win11_count.py --output "win11_analysis.md"
```

#### Usage Examples:
```sh
# Basic EUC summary validation (auto-detects data file)
python scripts/euc_summary.py

# With explicit data file path
python scripts/euc_summary.py data/raw/EUC_ESOL.xlsx

# Save output to file
python scripts/euc_summary.py --output summary.txt

# JSON format for automation
python scripts/euc_summary.py --format json --output metrics.json

# Quiet mode for automation
python scripts/euc_summary.py --quiet
```

### 8. ESOL Data Analysis
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
- `ESOL_Count_{category}_{timestamp}.md` - from `esol_count.py`
- `Kiosk_Count_{timestamp}.md` - from `kiosk_count.py`
- `Win11_Count_{timestamp}.md` - from `win11_count.py`
- `Executive_Summary_{timestamp}.md` - from `separated_esol_analyzer.py`
- `EUC_Summary_{timestamp}.txt` - from `euc_summary.py` (when using --output)
- `Quick_Status_{timestamp}.md` - from `separated_esol_analyzer.py`
- `ESOL_Analysis_{timestamp}.md` - from `esol-data-analysis-python.py`
- `OKR_Metrics_{timestamp}.json` - from `separated_esol_analyzer.py`

## 📁 Data File Management

### Smart File Detection
All analysis scripts now use intelligent file detection with the following priority:

1. **Explicit path**: `python script.py /path/to/data.xlsx`
2. **Environment variable**: `EUC_DATA_FILE=/path/to/data.xlsx`
3. **Default location**: `data/raw/EUC_ESOL.xlsx`
4. **CSV fallback**: `data/raw/EUC_ESOL.csv`

### Environment Variable Usage
```bash
# Set custom data file location
export EUC_DATA_FILE=/custom/path/EUC_data.xlsx

# All scripts will use this file automatically
python scripts/euc_summary.py
python scripts/win11_count.py
python scripts/kiosk_count.py
```

### Shared Data Utilities
**`scripts/data_utils.py`** - Common file handling functions:
- `get_data_file_path()` - Smart file resolution with fallbacks
- `add_data_file_argument()` - Standardized command-line arguments
- `validate_data_file()` - File validation and error handling

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

### `run_kiosk_analysis.bat` (NEW)
Kiosk EUC analysis with Windows 11 migration status:
```cmd
# Show help
.\run_kiosk_analysis.bat help

# Basic kiosk analysis (auto-saves to data/reports/)
.\run_kiosk_analysis.bat

# Custom output location
.\run_kiosk_analysis.bat custom_kiosk_report.md
```

### `run_win11_analysis.bat` (NEW)
Windows 11 EUC analysis and counting:
```cmd
# Show help
.\run_win11_analysis.bat help

# Basic Windows 11 analysis (auto-saves to data/reports/)
.\run_win11_analysis.bat

# Custom output location
.\run_win11_analysis.bat custom_win11_report.md
```

### `run_euc_summary.bat` (NEW)
EUC summary validation:
```cmd
# Show help
.\run_euc_summary.bat help

# Basic EUC summary validation (auto-detects data file)
.\run_euc_summary.bat

# With explicit data file
.\run_euc_summary.bat data/raw/EUC_ESOL.xlsx

# Save output to file
.\run_euc_summary.bat --output summary.txt

# JSON format for automation
.\run_euc_summary.bat --format json --output metrics.json
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