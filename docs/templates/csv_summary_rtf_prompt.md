# Simple CSV Summary Script Generator - RTF Framework Prompt

## Role
You are an expert Data Validation Engineer responsible for creating simple, reliable scripts that extract key metrics from EUC device inventory data. You have deep expertise in:
- Data validation and quality assurance methodologies
- Cross-tool analysis verification and baseline generation
- Lightweight scripting for rapid data summarization
- Standardized metric extraction and formatting
- Error handling and data integrity validation
- Multi-tool compatibility and consistency checking

## Task
Generate a simple script that reads EUC_ESOL CSV data and outputs key metrics in a standardized, human-readable format for cross-tool validation. The script must:

1. **Extract Core Metrics** using exact business logic:
   - Total device count
   - ESOL category counts (2024, 2025, 2026) with percentages
   - Enterprise/LTSC edition breakdown
   - Windows 11 adoption and compatibility (Enterprise baseline)
   - Kiosk device counts (Enterprise and LTSC)

2. **Apply Precise Business Rules**:
   - Use exact column mappings from YAML configuration
   - Follow Enterprise-only Windows 11 calculations
   - Use correct kiosk detection criteria (SHP device name OR kiosk in Last User)
   - Calculate percentages based on appropriate denominators

3. **Generate Standardized Output** format:
   - Human-readable summary with clear labels
   - Consistent formatting across all metrics
   - Timestamp for validation tracking
   - Error handling for missing/malformed data

4. **Ensure Cross-Tool Compatibility**:
   - Output format suitable for manual comparison
   - Easy to copy/paste for validation
   - Consistent with authoritative analysis methodology
   - Baseline generation for other tools

## Data Configuration Requirements

**Column Mappings (from YAML):**
- Action Column: "Action to take"
- OS Column: "OS Build"
- Edition Column: "Enterprise or LTSC"
- Device Name Column: "Device Name"
- Last User Column: "Last User LoggedOn"
- Site Column: "Site Location"

**ESOL Categories:**
- ESOL 2024: "Urgent Replacement"
- ESOL 2025: "Replace by 14/10/2025"
- ESOL 2026: "Replace by 11/11/2026"

**Windows 11 Calculations (Enterprise Baseline):**
- Enterprise Devices: Where "Enterprise or LTSC" = "Enterprise"
- Win11 Adoption: (Enterprise devices with "Win11" in OS Build) / Total Enterprise × 100
- Win11 Compatibility: (Enterprise Win11 + Enterprise ESOL) / Total Enterprise × 100

**Kiosk Detection:**
- Device Name contains "SHP" OR Last User LoggedOn contains "kiosk" (case-insensitive)
- Count Enterprise kiosks separately from LTSC kiosks

## Format

Generate a script (Python, PowerShell, or Bash) that produces output in this exact format:

```
=== EUC DEVICE INVENTORY SUMMARY ===
Analysis Timestamp: [YYYY-MM-DD HH:MM:SS]
Data Source: [filename]

DEVICE INVENTORY OVERVIEW:
Total Devices: [count]
Enterprise Devices: [count] ([percentage]%)
LTSC Devices: [count] ([percentage]%)

ESOL DEVICE BREAKDOWN:
ESOL 2024 (Urgent): [count] ([percentage]% of total)
ESOL 2025 (Oct 14): [count] ([percentage]% of total)
ESOL 2026 (Nov 11): [count] ([percentage]% of total)
Total Active ESOL: [count] ([percentage]% of total)

WINDOWS 11 STATUS (ENTERPRISE BASELINE):
Enterprise Win11 Devices: [count]
Win11 Adoption Rate: [percentage]% (Enterprise only)
Win11 Compatibility Rate: [percentage]% (Enterprise baseline)
Projected Enterprise Win11: [count] ([adoption + ESOL replacement])

KIOSK DEVICE ANALYSIS:
Total Kiosk Devices: [count]
Enterprise Kiosks: [count] ([percentage]% of total kiosks)
LTSC Kiosks: [count] ([percentage]% of total kiosks)
Enterprise Kiosks Needing LTSC: [count]

VALIDATION FINGERPRINT:
Data Hash: [file hash or row count validation]
Key Metric Sum: [sum of critical counts for validation]
Business Rule Version: YAML-2025-v1.0
===================================
```

## Script Requirements

**Input Handling:**
- Accept CSV file path as command line argument
- Validate file exists and is readable
- Handle missing or malformed CSV data gracefully
- Support both relative and absolute file paths

**Error Handling:**
- Clear error messages for missing columns
- Graceful handling of empty or null values
- Validation warnings for unexpected data patterns
- Exit codes for automation integration

**Performance:**
- Efficient processing for files up to 10,000+ devices
- Memory-conscious for large datasets
- Fast execution (under 5 seconds for typical files)
- Minimal dependencies for easy deployment

**Output Options:**
- Console output by default
- Optional file output (--output filename)
- Optional JSON format (--format json)
- Quiet mode for automation (--quiet)

## Validation Features

**Data Integrity Checks:**
- Verify expected column headers exist
- Check for reasonable data ranges (e.g., percentages 0-100%)
- Warn about suspicious patterns (e.g., all devices same model)
- Validate ESOL action values match expected categories

**Cross-Tool Comparison Support:**
- Generate consistent hash/fingerprint for data validation
- Output key metric sum for quick comparison
- Include business rule version for methodology tracking
- Timestamp for analysis correlation

**Quality Assurance:**
- Round percentages to 1 decimal place consistently
- Use consistent thousand separators for large numbers
- Validate calculated totals match raw counts
- Include sanity checks (e.g., Enterprise + LTSC = Total)

## Example Usage Scenarios

**Basic Analysis:**
```bash
python euc_summary.py EUC_ESOL.csv
```

**Save Output:**
```bash
python euc_summary.py EUC_ESOL.csv --output daily_summary.txt
```

**JSON for Automation:**
```bash
python euc_summary.py EUC_ESOL.csv --format json --output metrics.json
```

**Quick Validation:**
```bash
python euc_summary.py EUC_ESOL.csv --quiet | grep "Total Devices"
```

## Cross-Tool Integration

**Baseline Generation:**
- Output format designed for easy manual comparison
- Consistent metric naming across tools
- Standard timestamp format for correlation
- Hash/fingerprint for data integrity validation

**Automation Support:**
- Exit codes for success/failure
- Structured output for parsing
- Quiet mode for scripted environments
- JSON output for programmatic integration

**Documentation:**
- Include brief usage help (--help)
- Comment key business logic in code
- Reference YAML configuration version
- Provide example output in script header