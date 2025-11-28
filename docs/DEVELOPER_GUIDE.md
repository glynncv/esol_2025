# Developer Guide

## Overview

This guide helps developers work with the ESOL 2025 codebase, which follows a clean ETL (Extract, Transform, Load) architecture.

**Target Audience**: Developers adding new features, scripts, or analyses

## Quick Start

### Understanding the Architecture

```
scripts/
├── etl/                        # Reusable ETL modules
│   ├── load_data.py            # Data extraction and filtering
│   ├── analysis/               # Business logic
│   │   ├── esol_analyzer.py
│   │   ├── win11_analyzer.py
│   │   ├── kiosk_analyzer.py
│   │   └── burndown_calculator.py
│   └── presentation/           # Report formatting
│       ├── esol_formatter.py
│       ├── win11_formatter.py
│       ├── kiosk_formatter.py
│       ├── burndown_formatter.py
│       └── file_exporter.py
├── tests/                      # Unit tests
└── your_script.py              # Your analysis script
```

**Key Principle**: Separation of concerns
- **DataLoader**: Handles data loading and filtering (no calculations)
- **Analyzers**: Perform business logic calculations (no formatting)
- **Formatters**: Generate reports and output (no calculations)

## Creating a New Analysis Script

### Step 1: Create the Script Template

```python
#!/usr/bin/env python3
"""Description of your analysis."""
import argparse
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from separated_esol_analyzer import ConfigManager
from data_utils import add_data_file_argument
from etl.load_data import DataLoader
# Import existing analyzers or create your own
from etl.presentation import FileExporter

def main():
    """Main function."""
    # 1. Parse arguments
    parser = argparse.ArgumentParser(description='Your analysis description')
    add_data_file_argument(parser, 'Path to EUC_ESOL.xlsx file')
    parser.add_argument('--output', '-o', help='Output file')
    # Add your arguments
    args = parser.parse_args()

    # 2. Initialize components
    config_manager = ConfigManager()
    loader = DataLoader(config_manager)

    # 3. Load data (EXTRACT)
    df = loader.load_raw_data(args.data_file)

    # 4. Filter data as needed
    # Use existing filter methods or add your own logic
    filtered_df = loader.filter_enterprise_devices(df)

    # 5. Analyze data
    # Use existing analyzers or create custom calculations
    # YOUR ANALYSIS CODE HERE

    # 6. Format output
    # Use existing formatters or create custom formatting
    # YOUR FORMATTING CODE HERE

    # 7. Save and display
    print("Your console output")
    # saved_file = FileExporter.save_report(report, auto_prefix='YourReport')

if __name__ == "__main__":
    main()
```

### Step 2: Use Existing ETL Modules

**Data Loading**:
```python
from etl.load_data import DataLoader

loader = DataLoader(config_manager)

# Load raw data
df = loader.load_raw_data(args.data_file)

# Filter options:
esol_df = loader.filter_esol_devices(df, categories=['2024', '2025'])
enterprise_df = loader.filter_enterprise_devices(df, exclude_esol=True)
win11_df = loader.filter_win11_devices(df)
kiosk_df = loader.filter_kiosk_devices(df)
```

**Analysis**:
```python
from etl.analysis import ESOLAnalyzer, Win11Analyzer, KioskAnalyzer, BurndownCalculator

# ESOL Analysis
esol_analyzer = ESOLAnalyzer(config_manager)
counts = esol_analyzer.calculate_esol_counts(df)
percentages = esol_analyzer.calculate_esol_percentages(counts)
site_summary = esol_analyzer.generate_site_summary(esol_df)

# Win11 Analysis
win11_analyzer = Win11Analyzer(config_manager)
counts = win11_analyzer.calculate_win11_counts(enterprise_df)
kpi_metrics = win11_analyzer.calculate_kpi_metrics(counts)
site_summary = win11_analyzer.generate_site_summary(enterprise_df)

# Kiosk Analysis
kiosk_analyzer = KioskAnalyzer(config_manager)
counts = kiosk_analyzer.calculate_kiosk_counts(kiosk_df, total_devices)
ltsc_migration = kiosk_analyzer.calculate_ltsc_win11_migration(kiosk_df)

# Burndown
burndown_calc = BurndownCalculator(config_manager)
esol_burndown = burndown_calc.calculate_esol_burndown(esol_2024, esol_2025, esol_2026)
win11_burndown = burndown_calc.calculate_win11_burndown(total_eligible, completed)
```

**Presentation**:
```python
from etl.presentation import ESOLFormatter, Win11Formatter, KioskFormatter, BurndownFormatter, FileExporter

# Format reports
esol_report = ESOLFormatter.format_markdown_report(counts, percentages, category='all')
win11_report = Win11Formatter.format_markdown_report(counts, kpi_data=kpi_metrics)
kiosk_report = KioskFormatter.format_markdown_report(counts, ltsc_migration)

# Format console output
console = ESOLFormatter.format_console_summary(counts, percentages, category='all')
console = Win11Formatter.format_console_summary(counts, total_eligible, upgraded_pct, pending_count)
console = KioskFormatter.format_console_summary(counts, ltsc_migration)

# Save reports
saved_file = FileExporter.save_report(report, output_path=args.output, auto_prefix='MyReport')
json_file, csv_file = FileExporter.export_json_csv(data, file_prefix='my_data')
```

## Creating New ETL Modules

### Adding a New Analyzer

**File**: `scripts/etl/analysis/your_analyzer.py`

```python
"""Your analyzer description."""
from typing import Dict, Tuple
import pandas as pd
from pathlib import Path


class YourAnalyzer:
    """Analyze your specific metric.

    Pure business logic - no formatting or presentation.
    """

    def __init__(self, config_manager):
        """Initialize with configuration.

        Args:
            config_manager: ConfigManager instance
        """
        # Cache config values for performance
        self.esol_config = config_manager.get_esol_criteria()
        self.data_mapping = self.esol_config['data_mapping']

        # Cache column names
        self.action_col = self.data_mapping['action_column']
        self.os_col = self.data_mapping['os_column']
        # ... cache other columns as needed

    def calculate_your_metric(self, df: pd.DataFrame) -> Dict[str, any]:
        """Calculate your metric from DataFrame.

        Args:
            df: Filtered DataFrame to analyze

        Returns:
            Dictionary with calculation results:
            {
                'metric_1': value,
                'metric_2': value,
                ...
            }
        """
        # YOUR CALCULATION LOGIC HERE
        # Use self.action_col, self.os_col, etc. for column access

        return {
            'metric_1': 0,  # Replace with actual calculations
            'metric_2': 0
        }

    def generate_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate summary DataFrame.

        Args:
            df: DataFrame to summarize

        Returns:
            Summary DataFrame
        """
        # YOUR SUMMARY LOGIC HERE
        pass
```

**Update** `scripts/etl/analysis/__init__.py`:
```python
from .your_analyzer import YourAnalyzer

__all__ = ['ESOLAnalyzer', 'Win11Analyzer', 'KioskAnalyzer',
           'BurndownCalculator', 'YourAnalyzer']
```

### Adding a New Formatter

**File**: `scripts/etl/presentation/your_formatter.py`

```python
"""Your formatter description."""
from typing import Dict
from datetime import datetime


class YourFormatter:
    """Format your analysis results into reports.

    Pure presentation layer - no business logic or calculations.
    """

    @staticmethod
    def format_markdown_report(data: Dict) -> str:
        """Format analysis data into markdown report.

        Args:
            data: Dictionary from YourAnalyzer.calculate_your_metric()

        Returns:
            Formatted markdown report string
        """
        report_lines = []
        report_lines.append(
            f"# Your Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")
        report_lines.append(f"**Metric 1:** {data['metric_1']}")
        report_lines.append(f"**Metric 2:** {data['metric_2']}")
        report_lines.append("")

        return "\n".join(report_lines)

    @staticmethod
    def format_console_summary(data: Dict) -> str:
        """Format analysis data for console output.

        Args:
            data: Dictionary from YourAnalyzer.calculate_your_metric()

        Returns:
            Formatted string for console display
        """
        lines = []
        lines.append(f"Metric 1: {data['metric_1']}")
        lines.append(f"Metric 2: {data['metric_2']}")

        return "\n".join(lines)
```

**Update** `scripts/etl/presentation/__init__.py`:
```python
from .your_formatter import YourFormatter

__all__ = ['ESOLFormatter', 'Win11Formatter', 'KioskFormatter',
           'BurndownFormatter', 'FileExporter', 'YourFormatter']
```

## Working with Configuration

### Using ConfigManager

```python
from separated_esol_analyzer import ConfigManager

config_manager = ConfigManager()

# Get configuration dictionaries
esol_config = config_manager.get_esol_criteria()
win11_config = config_manager.get_win11_criteria()
okr_config = config_manager.get_okr_criteria()

# Access column mappings (always use these, never hardcode)
data_mapping = esol_config['data_mapping']
action_col = data_mapping['action_column']          # 'Action to take'
device_col = data_mapping['device_name_column']     # 'Device Name'
os_col = data_mapping['os_column']                  # 'EOSL Latest OS Build Supported'
site_col = data_mapping['site_column']              # 'Site Location'

# Access ESOL categories
esol_categories = esol_config['esol_categories']
esol_2024 = esol_categories['esol_2024']
target_date = esol_2024['target_date']              # '2025-06-30'
action_value = esol_2024['action_value']            # 'Urgent Replacement'

# Access Win11 criteria
win11_patterns = win11_config['win11_patterns']     # ['Win11']
kpi_target = win11_config['kpi_target_date']        # '2025-10-31'
```

### Adding New Configuration

**Edit** `config/your_criteria.yaml`:
```yaml
your_setting:
  threshold: 80
  categories:
    - category_1
    - category_2
```

**Update** `separated_esol_analyzer.py` ConfigManager if needed

## Testing Your Code

### Writing Unit Tests

**File**: `scripts/tests/test_your_module.py`

```python
"""Unit tests for YourAnalyzer."""
import unittest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.analysis.your_analyzer import YourAnalyzer


class TestYourAnalyzer(unittest.TestCase):
    """Test cases for YourAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock ConfigManager
        self.mock_config = Mock()
        self.mock_config.get_esol_criteria.return_value = {
            'data_mapping': {
                'action_column': 'Action',
                'os_column': 'OS',
                # ... other mappings
            }
        }

        self.analyzer = YourAnalyzer(self.mock_config)

    def test_basic_calculation(self):
        """Test basic metric calculation."""
        data = {'metric_1': 100, 'metric_2': 50}

        result = self.analyzer.calculate_your_metric(data)

        self.assertEqual(result['metric_1'], 100)
        self.assertEqual(result['metric_2'], 50)

    def test_edge_case_zero(self):
        """Test with zero values."""
        data = {'metric_1': 0, 'metric_2': 0}

        result = self.analyzer.calculate_your_metric(data)

        self.assertEqual(result['metric_1'], 0)
        # Assert expected behavior with zero values


if __name__ == '__main__':
    unittest.main()
```

### Running Tests

```bash
# Run all tests
cd scripts/tests
python3 run_tests.py

# Run specific test file
python3 -m unittest test_your_module.py

# Run with verbose output
python3 -m unittest test_your_module.py -v
```

## Best Practices

### 1. Always Use ConfigManager

**❌ Bad - Hardcoded column names**:
```python
esol_df = df[df['Action to take'].isin(['Urgent Replacement', ...])]
```

**✅ Good - Configuration-driven**:
```python
data_mapping = config_manager.get_esol_criteria()['data_mapping']
action_col = data_mapping['action_column']
esol_df = df[df[action_col].isin([...])]
```

### 2. Separate Concerns

**❌ Bad - Mixed responsibilities**:
```python
def analyze_data(df):
    # Calculate counts
    count = len(df)
    # Format report
    report = f"# Report\nCount: {count}"
    # Save file
    Path('report.md').write_text(report)
    return report
```

**✅ Good - Clean separation**:
```python
# In analyzer
def calculate_counts(df):
    return {'count': len(df)}

# In formatter
def format_report(counts):
    return f"# Report\nCount: {counts['count']}"

# In script
counts = analyzer.calculate_counts(df)
report = formatter.format_report(counts)
FileExporter.save_report(report, auto_prefix='Report')
```

### 3. Write Tests for Business Logic

Always write unit tests for:
- ✅ Calculation methods in analyzers
- ✅ Edge cases (zero values, empty DataFrames)
- ✅ Business logic branches

Don't need tests for:
- ⏭️ Simple formatters (just string concatenation)
- ⏭️ Data loading (tested through integration)

### 4. Use Type Hints

```python
from typing import Dict, List, Tuple
import pandas as pd

def calculate_metrics(df: pd.DataFrame) -> Dict[str, int]:
    """Calculate metrics from DataFrame."""
    return {'count': len(df)}

def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary DataFrame."""
    return df.groupby('Site').count()
```

### 5. Document Your Code

```python
def calculate_important_metric(df: pd.DataFrame, threshold: int = 100) -> Dict[str, int]:
    """Calculate important metric from device data.

    Args:
        df: DataFrame containing device data
        threshold: Minimum value for metric calculation (default: 100)

    Returns:
        Dictionary with metric results:
        {
            'total': Total count,
            'above_threshold': Count above threshold,
            'percentage': Percentage above threshold
        }

    Example:
        >>> counts = calculate_important_metric(df, threshold=50)
        >>> print(counts['total'])
        1000
    """
    # Implementation here
    pass
```

## Common Patterns

### Pattern 1: Site-Level Analysis

```python
def generate_site_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate site-level summary."""
    site_data = df.groupby(self.site_col).agg({
        'Device Name': 'count'
    }).rename(columns={'Device Name': 'Total_Devices'})

    # Add calculations
    site_data['Metric'] = site_data['Total_Devices'] * 2

    # Sort by total
    site_data = site_data.sort_values('Total_Devices', ascending=False)

    return site_data
```

### Pattern 2: Percentage Calculations

```python
def calculate_percentages(counts: Dict[str, int]) -> Dict[str, float]:
    """Calculate percentages from counts."""
    total = counts['total']

    return {
        'metric_pct': round((counts['metric'] / total) * 100, 2) if total > 0 else 0
    }
```

### Pattern 3: Burndown Calculations

```python
from datetime import datetime

def calculate_burndown(target_date: str, remaining_count: int) -> Dict:
    """Calculate burndown metrics."""
    target = datetime.strptime(target_date, '%Y-%m-%d')
    today = datetime.now()
    days_remaining = (target - today).days

    daily_rate = remaining_count / days_remaining if days_remaining > 0 else 0

    return {
        'days_remaining': max(0, days_remaining),
        'daily_burn_rate_needed': round(daily_rate, 2),
        'status': 'ON TRACK' if daily_rate < 1 else 'AT RISK'
    }
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'etl'`

**Solution**: Ensure scripts directory is in path:
```python
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
```

### Configuration Not Found

**Problem**: `FileNotFoundError: config/esol_criteria.yaml`

**Solution**: ConfigManager auto-generates defaults. Check `config/` directory exists.

### Column Not Found

**Problem**: `KeyError: 'Action to take'`

**Solution**: Always use ConfigManager for column names:
```python
data_mapping = config_manager.get_esol_criteria()['data_mapping']
action_col = data_mapping['action_column']
df[action_col]  # Use variable, not hardcoded string
```

## Examples

See these files for complete examples:
- `scripts/esol_count.py` - ESOL analysis
- `scripts/win11_count.py` - Windows 11 analysis
- `scripts/kiosk_count.py` - Kiosk analysis

## Further Reading

- `docs/ETL_ARCHITECTURE.md` - Complete architecture documentation
- `scripts/tests/README.md` - Testing guide
- `README.md` - User guide and feature overview

## Getting Help

1. Check existing scripts for patterns
2. Review ETL architecture documentation
3. Look at unit tests for usage examples
4. Check configuration files for available settings

---

**Last Updated:** November 2025
**Architecture Version:** 2.0 (Post-Restructure)
