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

Generates a comprehensive report and OKR metrics for all tracked devices.

```sh
python scripts/esol-data-analysis-python.py [filepath]
```
- If no filepath is provided, defaults to `data/raw/EUC_ESOL.xlsx`.
- Use `--output <file>` to save the report to a file.
- Use `--json` to output OKR metrics as JSON.

### 2026 Refresh Scope Script

Summarizes the number of devices in scope for the 2026 refresh (Action to take = "Replace by 11/11/2026"), by site and cost.

```sh
python scripts/euc_2026_count.py [filepath]
```
- If no filepath is provided, defaults to `data/raw/EUC_ESOL.xlsx`.
- Prints a table of devices and cost per site.
- Exports a CSV summary to `data/processed/euc_2026_site_summary.csv`.

## Output Files

- `data/processed/euc_2026_site_summary.csv` — Per-site summary of device count and replacement cost for 2026 refresh.

## Requirements

See `requirements.txt` for Python dependencies.

---

**Note:** Raw data files in `data/raw/` are not tracked in git for privacy and size reasons. Only processed exports in `data/processed/` are tracked. 