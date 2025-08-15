# ESOL EUC Device Data Analysis

This project provides tools to analyze End User Computing (EUC) device data for technical debt remediation, OKR tracking, and device refresh planning. It helps summarize device status, site-level needs, and cost projections for upcoming refresh cycles.

## Project Structure

- `scripts/` — Python scripts for analysis
- `data/raw/` — Raw input data (Excel files, not tracked in git)
- `data/processed/` — Processed outputs and exports (e.g., per-site summaries)
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

### 2. Simple ESOL Counter
**`euc_count.py`** - Simple device counting with category filtering

#### Usage Examples:
```sh
# All categories (default) - auto-saves to data/reports/
python scripts/euc_count.py

# Specific categories - auto-saves to data/reports/
python scripts/euc_count.py --category esol_2024
python scripts/euc_count.py --category esol_2025
python scripts/euc_count.py --category esol_2026

# Custom output location (optional)
python scripts/euc_count.py --output "my_custom_report.md"
```

### 3. Advanced OKR Analyzer
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

### 4. ESOL Data Analysis
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
- `ESOL_Count_{category}_{timestamp}.md` - from `euc_count.py`
- `Executive_Summary_{timestamp}.md` - from `separated_esol_analyzer.py`
- `Quick_Status_{timestamp}.md` - from `separated_esol_analyzer.py`
- `ESOL_Analysis_{timestamp}.md` - from `esol-data-analysis-python.py`
- `OKR_Metrics_{timestamp}.json` - from `separated_esol_analyzer.py`

## Batch Files (Windows)

### `run_dashboard.bat`
Launches the interactive OKR dashboard:
```cmd
.\run_dashboard.bat
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

Based on your latest analysis:
- **Total Devices**: 4,348
- **ESOL 2024**: 55 devices (1.26%) - 🔴 AT RISK
- **ESOL 2025**: 339 devices (7.80%) - 🔴 AT RISK
- **Windows 11 Compatibility**: 90.9% - 🟢 ON TRACK
- **Enterprise Kiosks**: 159 need re-provisioning

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