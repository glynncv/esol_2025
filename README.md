# ESOL EUC Device Data Analysis

This project provides tools to analyze End User Computing (EUC) device data for technical debt remediation, OKR tracking, and device refresh planning. It helps summarize device status, site-level needs, and cost projections for upcoming refresh cycles.

## Project Structure

- `scripts/` — Python scripts for analysis
- `data/raw/` — Raw input data (Excel files, not tracked in git)
- `data/processed/` — Processed outputs and exports (e.g., per-site summaries)
- `data/reports/` — (Optional) Reports and additional outputs

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

## Usage

### Main Analysis Script

**FIXED**: Now properly handles Unicode characters (emojis) when saving to files.

Generates a comprehensive report and OKR metrics for all tracked devices.

#### Command Line Usage

```sh
# Display report in console
python scripts/esol-data-analysis-python.py

# Save report to file
python scripts/esol-data-analysis-python.py --output report.md

# Output JSON metrics to console  
python scripts/esol-data-analysis-python.py --json

# Save JSON metrics to file
python scripts/esol-data-analysis-python.py --json --output metrics.json

# Use custom data file
python scripts/esol-data-analysis-python.py custom_data.xlsx --output custom_report.md
```

#### Batch File Helper (Windows)

For easier execution, use the provided batch file:

```cmd
# Show help
run_simple_analysis.bat help

# Generate report to console
run_simple_analysis.bat

# Save report to file (auto-timestamped)
run_simple_analysis.bat report

# Save report with custom name
run_simple_analysis.bat report my_report.md

# JSON metrics to console
run_simple_analysis.bat json

# Save JSON with custom name  
run_simple_analysis.bat jsave my_metrics.json
```

#### Features
- **UTF-8 encoding**: Properly handles emoji characters in reports
- **Flexible output**: Console display or file saving for both reports and JSON
- **Auto-timestamping**: Automatic filenames with timestamps when no name provided
- **OKR tracking**: Comprehensive Key Result progress monitoring
- **Site analysis**: Location-specific device breakdown
- **Cost calculations**: Replacement cost estimates

### EUC Device Count Script (Configuration-Driven)

**NEW**: Now supports YAML configuration for flexible ESOL category analysis.

Analyzes devices in scope for any ESOL refresh category (2024, 2025, 2026) using configuration-driven criteria.

#### Command Line Usage

```sh
# Analyze 2026 ESOL devices (default)
python scripts/euc_2026_count.py

# Analyze different ESOL categories
python scripts/euc_2026_count.py --category esol_2024
python scripts/euc_2026_count.py --category esol_2025
python scripts/euc_2026_count.py --category esol_2026

# Show available categories
python scripts/euc_2026_count.py --help-categories

# Custom configuration file
python scripts/euc_2026_count.py --config-path custom_config.yaml
```

#### Batch File Helper (Windows)

For easier execution, use the provided batch file:

```cmd
# Show help
run_euc_analysis.bat help

# Show available categories  
run_euc_analysis.bat cats

# Analyze specific years
run_euc_analysis.bat 2024
run_euc_analysis.bat 2025
run_euc_analysis.bat 2026
```

#### Configuration

The script uses `config/esol_criteria.yaml` to define:
- ESOL categories and their criteria
- Column mappings for data fields
- Target dates and descriptions
- Action values to filter on

Example configuration structure:
```yaml
esol_categories:
  esol_2024:
    description: "Critical devices requiring immediate replacement"
    action_value: "Urgent Replacement"
    target_date: "2025-06-30"
```

#### Features
- **Configuration-driven**: Easy to modify criteria without code changes
- **Multi-category support**: Analyze any defined ESOL category
- **Flexible output**: Customizable output paths and filenames
- **Validation**: Automatic validation of required columns and data
- **Cost calculation**: Automatic cost summaries by site and total
- **CSV export**: Per-site summary exports for further analysis

## Output Files

- `data/processed/euc_2026_site_summary.csv` — Per-site summary of device count and replacement cost for 2026 refresh.

## Requirements

See `requirements.txt` for Python dependencies.

---

**Note:** Raw data files in `data/raw/` are not tracked in git for privacy and size reasons. Only processed exports in `data/processed/` are tracked. #   e s o l _ 2 0 2 5 
 
 