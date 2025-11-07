# ESOL EUC Device Data Analysis

This project provides comprehensive tools to analyze End User Computing (EUC) device data for technical debt remediation, OKR tracking, device refresh planning, and Windows 11 migration. It helps summarize device status, site-level needs, cost projections, and burndown tracking for upcoming refresh cycles.

## 🚀 Quick Start

### **Unified Launcher: `analyze.bat`** (Recommended)
The primary way to use all tools:

```bash
# Show all available commands
.\analyze.bat help

# Launch interactive OKR dashboard
.\analyze.bat dashboard

# Windows 11 migration analysis
.\analyze.bat win11 --site-table --burndown

# ESOL replacement tracking
.\analyze.bat esol --site-table --burndown

# OKR tracker reports
.\analyze.bat okr

# Kiosk device analysis
.\analyze.bat kiosk

# Data validation summary
.\analyze.bat summary

# Export pending Win11 devices by site
.\analyze.bat export --site Gillingham
```

### Alternative: Direct Batch Files
```bash
# Launch the comprehensive OKR dashboard
.\run_dashboard.bat

# Windows 11 analysis
.\run_win11_analysis.bat --site-table --burndown

# ESOL analysis
.\run_esol_analysis.bat --site-table --burndown

# Other dedicated launchers
.\run_okr_tracker.bat
.\run_kiosk_analysis.bat
.\run_euc_summary.bat
```

## 📁 Project Structure

```
esol_2025/
├── scripts/                    # Python analysis scripts
├── config/                     # YAML configuration files
│   ├── esol_criteria.yaml      # ESOL categories, data mappings, kiosk detection
│   ├── okr_criteria.yaml       # OKR targets, weights, milestone dates
│   └── win11_criteria.yaml     # Windows 11 eligibility, upgrade logic, KPI targets
├── data/
│   ├── raw/                    # Input Excel files (not tracked in git)
│   ├── processed/              # Exported CSV/JSON data
│   └── reports/                # Auto-generated reports
├── notebooks/                  # Jupyter notebooks for analysis
├── run_*.bat                   # Windows batch file launchers
└── requirements.txt            # Python dependencies
```

## 🎯 Key Features

### **Windows 11 Migration Tracking**
- **KPI Target**: 100% of eligible EUCs upgraded by Oct 31, 2025
- **Site-level breakdown**: Track progress by location
- **Burndown analysis**: Daily burn rate calculations and risk assessment
- **Scope**: Enterprise devices only (excludes LTSC and ESOL replacement devices)

### **ESOL Replacement Management**
- **Multi-category tracking**: ESOL 2024 (Jun 30), ESOL 2025 (Oct 14), ESOL 2026 (Nov 11)
- **Site prioritization**: Identify high-impact locations
- **Cost analysis**: Replacement budget planning
- **Burndown tracking**: Daily replacement rate monitoring

### **OKR Dashboard**
- **Interactive interface**: Easy-to-use menu system
- **Quick status checks**: Daily progress monitoring
- **Executive summaries**: Management-ready reports
- **Site analysis**: Both ESOL and Windows 11 site breakdowns

### **Site-Specific Windows 11 Export**
- **Pending device export**: Get detailed list of Windows 11 pending devices for any site
- **Console summary**: Quick overview of eligible, upgraded, and pending counts
- **CSV export**: Detailed device information for upgrade planning
- **Site listing**: See all available sites at a glance

## ⚙️ Configuration

The project uses a modular YAML configuration system:

### **Configuration Files**
- **`config/esol_criteria.yaml`**: ESOL categories, data mappings, kiosk detection
- **`config/okr_criteria.yaml`**: OKR targets, weights, milestone dates
- **`config/win11_criteria.yaml`**: Windows 11 eligibility, upgrade logic, KPI targets

### **Windows 11 Eligibility Logic**
```yaml
# Windows 11 eligibility criteria (all must be met):
# 1. LTSC or Enterprise = "Enterprise" (only Enterprise devices targeted)
# 2. EOSL Latest OS Build Supported contains "Win11" (device capability)
# 3. Action to take is any EXCEPT ESOL 2024 or ESOL 2025 (exclude replacement devices)
```

### **Data Column Mappings**
- **Eligibility**: `EOSL Latest OS Build Supported` (device capability)
- **Upgrade Status**: `Current OS Build` (actual installation)
- **Site Location**: `Site Location`
- **Device Edition**: `LTSC or Enterprise`

## 🛠️ Setup

1. **Clone and install**:
   ```bash
   git clone <your-repo-url>
   cd esol_2025
   pip install -r requirements.txt
   ```

2. **Add your data**:
   - Place `EUC_ESOL.xlsx` in `data/raw/`
   - Or set environment variable: `EUC_DATA_FILE=/path/to/your/data.xlsx`

## 📊 Analysis Scripts

### 1. **OKR Dashboard** (`okr_dashboard.py`)
**Interactive dashboard for comprehensive analysis**

**Features:**
- Quick status check (daily use)
- Executive summary (management reports)
- Full OKR tracker (comprehensive analysis)
- Site analysis (ESOL and Windows 11)
- Save executive reports with timestamps

**Usage:**
```bash
python scripts/okr_dashboard.py
# or
.\run_dashboard.bat
```

### 2. **Windows 11 Analysis** (`win11_count.py`)
**Windows 11 migration tracking and KPI monitoring**

**Features:**
- **KPI Tracking**: 100% eligible EUCs by Oct 31, 2025
- **Site Analysis**: Progress by location (`--site-table`)
- **Burndown Analysis**: Daily burn rates and risk assessment (`--burndown`)
- **Scope**: Enterprise devices only (excludes ESOL replacement)

**Usage:**
```bash
# Basic analysis
python scripts/win11_count.py

# With site breakdown
python scripts/win11_count.py --site-table

# With burndown analysis
python scripts/win11_count.py --burndown

# Both site and burndown
python scripts/win11_count.py --site-table --burndown

# Batch files
.\run_win11_analysis.bat --site-table --burndown
.\run_win11_burndown.bat
```

### 3. **ESOL Analysis** (`esol_count.py`)
**ESOL replacement tracking and site management**

**Features:**
- **Multi-category tracking**: ESOL 2024, 2025, 2026
- **Site Analysis**: Device counts and costs by location (`--site-table`)
- **Burndown Analysis**: Daily replacement rates (`--burndown`)
- **Category filtering**: Focus on specific ESOL years

**Usage:**
```bash
# All categories
python scripts/esol_count.py

# Specific category
python scripts/esol_count.py --category esol_2024

# With site breakdown
python scripts/esol_count.py --site-table

# With burndown analysis
python scripts/esol_count.py --burndown

# Both site and burndown
python scripts/esol_count.py --site-table --burndown

# Batch files
.\run_esol_analysis.bat --site-table --burndown
.\run_esol_burndown.bat
```

### 4. **OKR Tracker** (`okr_tracker.py`)
**Professional OKR tracking with comprehensive reporting**

**Features:**
- Weighted scoring system (KR1: 25%, KR2: 25%, KR3: 40%, KR4: 10%)
- Progress visualization with status indicators
- Baseline tracking for historical progress
- Financial impact analysis
- Site prioritization

**Usage:**
```bash
# Basic OKR report
python scripts/okr_tracker.py

# Monthly report
.\run_okr_tracker.bat monthly

# Compare with previous data
.\run_okr_tracker.bat compare previous_metrics.json
```

### 5. **Kiosk Analysis** (`kiosk_count.py`)
**Kiosk device analysis and Windows 11 migration**

**Features:**
- Kiosk detection using configurable patterns
- Enterprise vs LTSC breakdown
- Windows 11 migration analysis
- Auto-saves reports to data/reports/

**Usage:**
```bash
python scripts/kiosk_count.py
# or
.\run_kiosk_analysis.bat
```

### 6. **EUC Summary** (`euc_summary.py`)
**Cross-tool validation and standardized metrics**

**Features:**
- Standardized metrics extraction
- Multiple output formats (text, JSON)
- Data integrity validation
- Smart file detection

**Usage:**
```bash
python scripts/euc_summary.py
# or
.\run_euc_summary.bat
```

### 7. **Export Pending Windows 11 Devices** (`scripts/export_site_win11_pending.py`)
**Export detailed pending Windows 11 devices for any site**

**Features:**
- Site-specific Windows 11 pending device export
- Detailed console summary with eligibility breakdown
- CSV export with all device details
- List all available sites
- Auto-generates timestamped filenames

**Usage:**
```bash
# List all available sites
python scripts/export_site_win11_pending.py --list-sites

# Export for default site (Gillingham)
python scripts/export_site_win11_pending.py

# Export for a specific site
python scripts/export_site_win11_pending.py --site Blois
python scripts/export_site_win11_pending.py --site "Rzeszow, Poland"

# Custom output filename
python scripts/export_site_win11_pending.py --site Iasi --output iasi_pending.csv

# Show help
python scripts/export_site_win11_pending.py --help
```

**Output:**
- Console report showing total devices, Win11 eligible, upgraded, and pending counts
- CSV file with all device columns for detailed analysis (auto-saved to `data/processed/`)
- Percentages showing eligibility rate and upgrade progress

## 🎯 OKR Framework

### **Key Results Tracked**
1. **KR1**: ESOL 2024 remediation (0% target by June 30, 2025)
2. **KR2**: ESOL 2025 remediation (50% milestone by June 30, 100% by Dec 31, 2025)
3. **KR3**: Windows 11 compatibility (90% target by October 31, 2025)
4. **KR4**: Enterprise kiosk LTSC re-provisioning (0 devices by June 30, 2025)

### **Scoring System**
- **Weighted scoring**: KR1 (25%), KR2 (25%), KR3 (40%), KR4 (10%)
- **Status levels**: 🟢 ON TRACK, 🟡 CAUTION, 🔴 AT RISK
- **Progress visualization**: Progress bars and color-coded indicators

## 📈 Burndown Analysis

### **Windows 11 Burndown**
- **Target**: 100% of eligible EUCs by Oct 31, 2025
- **Risk levels**: HIGH (>1 device/day), MEDIUM (0.5-1 device/day), LOW (<0.5 device/day)
- **Daily burn rate**: Calculated based on remaining devices and days

### **ESOL Burndown**
- **Multi-category**: Separate tracking for 2024, 2025, 2026 deadlines
- **Risk assessment**: Based on daily replacement rates needed
- **Site prioritization**: Focus on high-impact locations

## 📁 Auto-Save Reports

**All scripts automatically save reports to `data/reports/` with timestamped filenames:**

- `Win11_Count_{timestamp}.md` - Windows 11 analysis
- `Win11_Burndown_{timestamp}.md` - Windows 11 burndown
- `ESOL_Count_{category}_{timestamp}.md` - ESOL analysis
- `ESOL_Burndown_{timestamp}.md` - ESOL burndown
- `OKR_Tracker_{timestamp}.md` - OKR tracking
- `Executive_Summary_{timestamp}.md` - Executive summaries

**Export pending Windows 11 devices for site-specific analysis:**

- `{site_name}_pending_win11_{timestamp}.csv` - Site-specific pending device export (saved to `data/processed/`)

## 📊 Data Exports

**Site analysis data automatically exported to `data/processed/`:**

- **CSV Format**: Excel/Sheets compatible
- **JSON Format**: API/programmatic use
- **Data Includes**: Device counts, costs, percentages by site
- **Auto-generated**: Created with `--site-table` option

## 🔧 Configuration

### **ESOL Criteria** (`config/esol_criteria.yaml`)
- ESOL category definitions and target dates
- Windows 11 compatibility settings
- Kiosk detection patterns
- Data column mappings

### **OKR Criteria** (`config/okr_criteria.yaml`)
- OKR targets and milestones
- Scoring weights and thresholds
- Progress tracking settings

## 🖥️ Launchers

### **Unified Launcher: `analyze.bat`** (Recommended)
One command to rule them all:
```bash
analyze.bat [command] [options]
```

**Commands:**
- `dashboard` - Launch interactive OKR dashboard
- `win11` - Windows 11 migration analysis
- `esol` - ESOL replacement tracking
- `okr` - OKR tracker reports
- `kiosk` - Kiosk device analysis
- `summary` - Data validation summary
- `export` - Export pending Win11 devices by site
- `help` - Show help message

### Individual Batch Files (Alternative)

| File | Purpose | Usage |
|------|---------|-------|
| `run_dashboard.bat` | Interactive OKR dashboard | `.\run_dashboard.bat` |
| `run_win11_analysis.bat` | Windows 11 analysis | `.\run_win11_analysis.bat --site-table --burndown` |
| `run_win11_burndown.bat` | Windows 11 burndown only | `.\run_win11_burndown.bat` |
| `run_esol_analysis.bat` | ESOL analysis | `.\run_esol_analysis.bat --site-table --burndown` |
| `run_esol_burndown.bat` | ESOL burndown only | `.\run_esol_burndown.bat` |
| `run_okr_tracker.bat` | OKR tracking | `.\run_okr_tracker.bat monthly` |
| `run_kiosk_analysis.bat` | Kiosk analysis | `.\run_kiosk_analysis.bat` |
| `run_euc_summary.bat` | EUC summary validation | `.\run_euc_summary.bat` |

## 📋 Requirements

- Python 3.8+
- pandas
- openpyxl
- pyyaml

Install with:
```bash
pip install -r requirements.txt
```

## 🎯 Current Status (Example)

Based on recent analysis:
- **Total Devices**: 4,098
- **Windows 11 Eligible**: 3,632 (excluding ESOL replacement)
- **Windows 11 Upgraded**: 3,489 (96.1%)
- **Windows 11 Pending**: 143 devices (3.9%)
- **ESOL 2024**: 8 devices (urgent)
- **ESOL 2025**: 171 devices (planned)
- **ESOL 2026**: 258 devices (future)

## 🚀 Getting Started

1. **Quick Start**: Run `.\analyze.bat dashboard` or `.\analyze.bat help` to see all options
2. **Windows 11 Focus**: Use `.\analyze.bat win11 --burndown` for migration tracking
3. **ESOL Focus**: Use `.\analyze.bat esol --burndown` for replacement planning
4. **Daily Monitoring**: Use `.\analyze.bat dashboard` for quick status checks
5. **Site Export**: Use `.\analyze.bat export --site [SiteName]` for pending Win11 devices

## 📞 Support

For questions or issues:
1. Check the unified launcher help: `.\analyze.bat help`
2. Review the configuration files in `config/`
3. Check the auto-generated reports in `data/reports/`