# Code Extraction Examples: From-To Mapping

## Example 1: Column Mapping Consolidation

### BEFORE (okr_tracker.py, lines 42-56 - BAD PATTERN)
```python
def load_data(self) -> pd.DataFrame:
    """Load Excel data and standardize column names"""
    try:
        # Hardcoded column mapping - DUPLICATED in 3 other scripts!
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
        # ... rename columns ...
        return self.data
```

### AFTER (Use ConfigManager - GOOD PATTERN)
```python
# From separated_esol_analyzer.py ConfigManager class
def load_data(filepath: str) -> pd.DataFrame:
    """Load Excel data - NO MAPPING, just pass-through"""
    df = pd.read_excel(filepath, sheet_name='Export')
    self._validate_data_columns(df)  # Validate against config schema
    return df  # Return raw DataFrame with original column names

# All scripts then use ConfigManager:
config = ConfigManager()
data_mapping = config.get_esol_criteria()['data_mapping']
action_col = data_mapping['action_column']  # 'Action to take'
```

### CONFIG (config/esol_criteria.yaml - SINGLE SOURCE OF TRUTH)
```yaml
data_mapping:
  action_column: 'Action to take'
  os_column: 'OS Build'
  current_os_column: 'Current OS Build'
  edition_column: 'LTSC or Enterprise'
  device_name_column: 'Device Name'
  cost_column: 'Cost for Replacement $'
  user_columns:
    current: 'Current User Logged On'
    last: 'Last User Logged On'
```

**Impact**: Remove 150+ lines of duplicate mapping code, centralize configuration

---

## Example 2: Burndown Logic Extraction

### BEFORE (esol_count.py, lines 153-198 - EMBEDDED IN MAIN)
```python
def main():
    # ... setup code ...
    
    if args.burndown:
        # Burndown calculation MIXED WITH REPORT GENERATION
        esol_2024_date = datetime.strptime(
            esol_config['esol_categories']['esol_2024']['target_date'], 
            '%Y-%m-%d'
        )
        esol_2025_date = datetime.strptime(
            esol_config['esol_categories']['esol_2025']['target_date'], 
            '%Y-%m-%d'
        )
        
        current_date = datetime.now()
        
        # Calculate burndown metrics for each category
        days_remaining_2024 = (esol_2024_date - current_date).days
        daily_burn_rate_2024 = esol2024 / days_remaining_2024 if days_remaining_2024 > 0 else 0
        
        burndown_data.append({
            'category': 'ESOL 2024',
            'target_date': esol_config['esol_categories']['esol_2024']['target_date'],
            'days_remaining': int(days_remaining_2024),
            'remaining_devices': int(esol2024),
            'daily_burn_rate_needed': round(daily_burn_rate_2024, 2),
            'status': 'AT RISK' if days_remaining_2024 <= 30 else 'ON TRACK'
        })
        
        # ... more similar code for 2025, 2026 ...
        # ... then format and export ...
```

### AFTER (Extract to analysis/burndown_calculator.py - REUSABLE)
```python
# New file: scripts/analysis/burndown_calculator.py

class BurndownCalculator:
    """Calculate burndown metrics for time-based ESOL categories"""
    
    def __init__(self, config: ConfigManager):
        self.esol_config = config.get_esol_criteria()
    
    def calculate_burndown(self, category: str, remaining_devices: int) -> Dict[str, Any]:
        """
        Calculate burndown metrics for a single category.
        
        Args:
            category: 'esol_2024', 'esol_2025', or 'esol_2026'
            remaining_devices: Number of devices still needing replacement
        
        Returns:
            Dict with days_remaining, burn_rate, status, etc.
        """
        target_date = datetime.strptime(
            self.esol_config['esol_categories'][category]['target_date'],
            '%Y-%m-%d'
        )
        current_date = datetime.now()
        
        days_remaining = (target_date - current_date).days
        daily_burn_rate = (
            remaining_devices / days_remaining 
            if days_remaining > 0 
            else float('inf')
        )
        
        # Determine status based on burn rate thresholds
        if daily_burn_rate > 1:
            status = 'AT RISK'
        elif daily_burn_rate > 0.5:
            status = 'CAUTION'
        else:
            status = 'ON TRACK'
        
        return {
            'category': category,
            'target_date': self.esol_config['esol_categories'][category]['target_date'],
            'days_remaining': max(0, days_remaining),
            'remaining_devices': remaining_devices,
            'daily_burn_rate_needed': round(daily_burn_rate, 2),
            'status': status
        }
    
    def calculate_all_burndown(self, counts: Dict[str, int]) -> List[Dict[str, Any]]:
        """Calculate burndown for all ESOL categories"""
        burndown_data = []
        for category in ['esol_2024', 'esol_2025', 'esol_2026']:
            data = self.calculate_burndown(category, counts[f'{category}_count'])
            burndown_data.append(data)
        return burndown_data
```

### THEN USE IN esol_count.py (NOW THIN WRAPPER)
```python
def main():
    # ... setup code ...
    
    if args.burndown:
        # Now just 3 lines instead of 45!
        calculator = BurndownCalculator(config)
        burndown_data = calculator.calculate_all_burndown(counts)
        formatter = BurndownReportFormatter(config)
        report = formatter.format(burndown_data)
        # ... export report ...
```

**Impact**: 
- Remove 45 lines from esol_count.py (can reuse in win11_count.py)
- Add 70 lines to new BurndownCalculator (reusable by 2 scripts = 40 line savings each)
- Same logic now testable in isolation

---

## Example 3: Site Aggregation Consolidation

### BEFORE (esol_count.py, lines 47-66 - MONOLITHIC)
```python
if args.site_table:
    # Generate site summary table
    esol_df = df[df[action_col].isin(all_esol_actions)]

    # Group by site and calculate counts and costs
    site_data = esol_df.groupby(site_col).agg({
        action_col: lambda x: (x == esol_2024_action).sum(),
        cost_col: 'sum'
    }).rename(columns={action_col: 'ESOL_2024_Count', cost_col: 'Total_Cost'})

    site_data['ESOL_2025_Count'] = esol_df.groupby(site_col)[action_col].apply(
        lambda x: (x == esol_2025_action).sum()
    )
    site_data['ESOL_2026_Count'] = esol_df.groupby(site_col)[action_col].apply(
        lambda x: (x == esol_2026_action).sum()
    )
    site_data['Total_ESOL'] = (
        site_data['ESOL_2024_Count'] + 
        site_data['ESOL_2025_Count'] + 
        site_data['ESOL_2026_Count']
    )
    
    site_data = site_data[['ESOL_2024_Count', 'ESOL_2025_Count', 'ESOL_2026_Count', 'Total_ESOL', 'Total_Cost']]
    site_data = site_data[site_data['Total_ESOL'] > 0].sort_values('Total_ESOL', ascending=False)
```

### AFTER (Extract to analysis/esol_analyzer.py - REUSABLE)
```python
# New file: scripts/analysis/esol_analyzer.py

class ESOLAnalyzer:
    """Analyze ESOL data at device and site levels"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.data_analyzer = DataAnalyzer(config)
    
    def get_site_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get site-level ESOL summary with costs.
        
        Returns DataFrame with columns:
        - ESOL_2024_Count
        - ESOL_2025_Count  
        - ESOL_2026_Count
        - Total_ESOL
        - Total_Cost (if cost column exists)
        """
        esol_config = self.config.get_esol_criteria()
        data_mapping = esol_config['data_mapping']
        
        action_col = data_mapping['action_column']
        site_col = data_mapping['site_column']
        cost_col = data_mapping.get('cost_column')
        
        # Get action values from config
        esol_2024_action = esol_config['esol_categories']['esol_2024']['action_value']
        esol_2025_action = esol_config['esol_categories']['esol_2025']['action_value']
        esol_2026_action = esol_config['esol_categories']['esol_2026']['action_value']
        all_esol_actions = [esol_2024_action, esol_2025_action, esol_2026_action]
        
        # Filter ESOL devices
        esol_df = df[df[action_col].isin(all_esol_actions)]
        
        # Build site summary
        site_data = pd.DataFrame({
            'ESOL_2024_Count': esol_df[esol_df[action_col] == esol_2024_action].groupby(site_col).size(),
            'ESOL_2025_Count': esol_df[esol_df[action_col] == esol_2025_action].groupby(site_col).size(),
            'ESOL_2026_Count': esol_df[esol_df[action_col] == esol_2026_action].groupby(site_col).size(),
        }).fillna(0).astype(int)
        
        site_data['Total_ESOL'] = (
            site_data['ESOL_2024_Count'] + 
            site_data['ESOL_2025_Count'] + 
            site_data['ESOL_2026_Count']
        )
        
        if cost_col and cost_col in df.columns:
            site_data['Total_Cost'] = esol_df.groupby(site_col)[cost_col].sum()
        
        # Filter and sort
        site_data = site_data[site_data['Total_ESOL'] > 0].sort_values('Total_ESOL', ascending=False)
        
        return site_data
```

### THEN USE IN esol_count.py (NOW 3 LINES)
```python
if args.site_table:
    analyzer = ESOLAnalyzer(config)
    site_data = analyzer.get_site_summary(df)
    # ... export to CSV/JSON ...
```

**Impact**: Move 20 lines of complex aggregation to reusable class, simplify script

---

## Example 4: Formatting Extraction

### BEFORE (win11_count.py, lines 200+ - MIXED WITH LOGIC)
```python
def main():
    # ... all the calculations ...
    
    # Mixed report generation
    report_lines = [
        f"# Windows 11 Migration Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"**Total devices analyzed:** {total_devices:,}",
        "",
    ]
    
    # Detailed table
    report_lines.append("## Migration Status by Site")
    report_lines.append("")
    report_lines.append("|Site|Total Enterprise|Win11 Capable|Current Win11|Pending|%Eligible|% Complete|")
    report_lines.append("|---|---|---|---|---|---|---|")
    
    for site, row in site_data.iterrows():
        # Formatting logic directly in main
        pct_eligible = (row['Win11_Eligible_Count'] / row['Total_Devices'] * 100) if row['Total_Devices'] > 0 else 0
        pct_complete = (row['Win11_Count'] / row['Win11_Eligible_Count'] * 100) if row['Win11_Eligible_Count'] > 0 else 0
        
        report_lines.append(
            f"|{site}|{int(row['Total_Devices'])}|{int(row['Win11_Eligible_Count'])}|"
            f"{int(row['Win11_Count'])}|{int(row['Pending_Count'])}|{pct_eligible:.1f}%|{pct_complete:.1f}%|"
        )
```

### AFTER (Extract to presentation/win11_formatter.py - REUSABLE)
```python
# New file: scripts/presentation/win11_formatter.py

class Win11ReportFormatter:
    """Format Windows 11 migration metrics into readable reports"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def format_site_summary_table(self, site_data: pd.DataFrame) -> str:
        """Format site summary as Markdown table"""
        lines = []
        lines.append("## Migration Status by Site")
        lines.append("")
        lines.append("|Site|Total Enterprise|Win11 Capable|Current Win11|Pending|%Eligible|% Complete|")
        lines.append("|---|---|---|---|---|---|---|")
        
        for site, row in site_data.iterrows():
            # Formatting logic in dedicated class
            pct_eligible = self._safe_percentage(
                row['Win11_Eligible_Count'], 
                row['Total_Devices']
            )
            pct_complete = self._safe_percentage(
                row['Win11_Count'], 
                row['Win11_Eligible_Count']
            )
            
            lines.append(
                f"|{site}|{int(row['Total_Devices'])}|{int(row['Win11_Eligible_Count'])}|"
                f"{int(row['Win11_Count'])}|{int(row['Pending_Count'])}|{pct_eligible:.1f}%|{pct_complete:.1f}%|"
            )
        
        return "\n".join(lines)
    
    @staticmethod
    def _safe_percentage(numerator: int, denominator: int) -> float:
        """Calculate percentage safely (avoid division by zero)"""
        return (numerator / denominator * 100) if denominator > 0 else 0
```

### THEN USE IN win11_count.py (PURE PRESENTATION)
```python
def main():
    # ... calculations only ...
    
    # Pure formatting
    formatter = Win11ReportFormatter(config)
    site_table = formatter.format_site_summary_table(site_data)
    
    lines = [
        f"# Windows 11 Migration Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"**Total devices analyzed:** {total_devices:,}",
        "",
        site_table,
    ]
```

**Impact**: Move formatting logic to reusable class, enable theming/style changes in one place

---

## Example 5: Analysis Pipeline Pattern

### BEFORE (Each script does everything in main)
```python
# esol_count.py, win11_count.py, kiosk_count.py - EACH DUPLICATES THIS
def main():
    args = parser.parse_args()
    data_file = get_data_file_path(args.data_file)
    validate_data_file(data_file)
    df = pd.read_excel(data_file)  # DUPLICATE #1
    
    # Get config and columns
    config_manager = ConfigManager()  # DUPLICATE #2
    esol_config = config_manager.get_esol_criteria()
    data_mapping = esol_config['data_mapping']
    
    action_col = data_mapping['action_column']  # DUPLICATE #3
    # ... more column setup ...
    
    # Filtering and counting (DUPLICATE #4)
    esol_2024_count = (df[action_col] == esol_2024_action).sum()
    esol_2025_count = (df[action_col] == esol_2025_action).sum()
    
    # Calculate percentages (DUPLICATE #5)
    esol_2024_pct = (esol_2024_count / len(df)) * 100
    
    # Format report (DUPLICATE #6)
    report_lines = [f"# Report\n", ...]
    
    # Export to file
    output_path.write_text(report_content)
```

### AFTER (Thin wrappers following standard pipeline)
```python
# Template: scripts/analysis_script.py
# Used by: esol_count.py, win11_count.py, kiosk_count.py, etc.

def main():
    # Step 1: Parse arguments (UNIQUE TO EACH SCRIPT)
    args = parser.parse_args()
    
    # Step 2: Load data (SHARED)
    config = ConfigManager()
    analyzer = DataAnalyzer(config)
    df = analyzer.load_data(get_data_file_path(args.data_file))
    
    # Step 3: Run analysis (DOMAIN-SPECIFIC)
    if 'esol' in sys.argv[0]:
        domain_analyzer = ESOLAnalyzer(config)
        results = domain_analyzer.analyze(df, args)
    elif 'win11' in sys.argv[0]:
        domain_analyzer = Win11Analyzer(config)
        results = domain_analyzer.analyze(df, args)
    elif 'kiosk' in sys.argv[0]:
        domain_analyzer = KioskAnalyzer(config)
        results = domain_analyzer.analyze(df, args)
    
    # Step 4: Format output (DOMAIN-SPECIFIC)
    formatter = get_formatter(domain_analyzer.__class__.__name__, config)
    report = formatter.format(results)
    
    # Step 5: Export (SHARED)
    exporter = FileExporter(config)
    exporter.export(report, args.output, args.format)

if __name__ == "__main__":
    main()
```

**Impact**: Replace 5 similar scripts with unified pattern, reduce duplication by 70%

---

## Summary: Before → After Comparison

| Aspect | BEFORE | AFTER | Benefit |
|--------|--------|-------|---------|
| **Column Mapping** | 5 copies of 13-item mapping | 1 ConfigManager entry | Single source of truth |
| **Burndown Logic** | 45 lines in esol_count.py + 40 lines in win11_count.py | 70 lines in shared class | Reuse + testability |
| **Site Aggregation** | 20 lines in esol_count.py | 50 lines in ESOLAnalyzer | Organized + reusable |
| **Formatting** | 40+ lines spread in each script | 80 lines in Win11Formatter | Consistent theming |
| **Main Flow** | 300-400 lines per script | 40-50 lines per script | Readability + maintenance |
| **Test Coverage** | 0% (monolithic) | >70% (isolated modules) | Confidence + stability |

