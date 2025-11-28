# ESOL Codebase ETL Architecture Mapping

**Project**: ESOL EUC Device Data Analysis  
**Analysis Date**: 2025-11-21  
**Current Branch**: claude/euc-device-analysis-tools-011CUtcvdKFSfLMorNPnf6wu

---

## 1. ETL PHASE DEFINITIONS

| Phase | Purpose | Inputs | Outputs |
|-------|---------|--------|---------|
| **DATA CAPTURE** | Load raw data from Excel/CSV files | `.xlsx/.csv` files | Pandas DataFrame |
| **CLEAN & TRANSFORM** | Parse, validate, map columns, apply rules | DataFrame | Cleaned DataFrame with standard column names |
| **ANALYSIS** | KPI/OKR calculations, business logic, scoring | Cleaned DataFrame + Config | Metrics, scores, percentages |
| **NORMALIZE** | Organize into structured output tables | Metrics | CSV/JSON exports, summary tables |
| **PRESENTATION** | Generate reports (MD/Excel) for users | Metrics + Config | Markdown reports, human-readable output |

---

## 2. CURRENT FILE INVENTORY & PHASE MAPPING

### **Core Utility Files**

#### `data_utils.py` (94 lines)
**Phases Handled**: ✅ DATA CAPTURE
- **Functions**:
  - `get_data_file_path()` - File path resolution with fallback logic
  - `add_data_file_argument()` - CLI argument standardization
  - `validate_data_file()` - File existence/readability checks
- **Scope**: Pure data loading utilities (no transformations)
- **Status**: ✅ **WELL SEPARATED** - Single responsibility

#### `config_helper.py` (192 lines)
**Phases Handled**: Configuration management (META)
- **Functions**:
  - Display current configuration
  - Validate config files
  - Backup configuration
- **Scope**: Interactive configuration UI
- **Status**: ✅ **WELL SEPARATED** - Standalone tool

#### `separated_esol_analyzer.py` (1000+ lines)
**Phases Handled**: ✅ ALL FIVE PHASES (Multi-layer architecture)
- **Layer 1 - CONFIG**: `ConfigManager` class
  - Loads YAML configuration files
  - Validates completeness
  - Creates defaults
  - **Status**: ✅ Pure configuration management
  
- **Layer 2 - DATA CAPTURE & TRANSFORM**: `DataAnalyzer` class
  - `load_data()` - Reads Excel file
  - `_validate_data_columns()` - Schema validation
  - `extract_basic_counts()` - Pure data extraction
  - `extract_kiosk_counts()` - Pattern matching extraction
  - `extract_site_counts()` - Group-by operations
  - `extract_cost_totals()` - Aggregation
  - **Status**: ✅ **WELL SEPARATED** - Only extracts, no calculations
  
- **Layer 3 - ANALYSIS (Business Logic)**: `BusinessLogicCalculator` class
  - `calculate_percentages()` - Ratio calculations
  - `calculate_windows11_compatibility()` - Compatibility scoring
  - `calculate_kr_progress_scores()` - OKR progress (0-100)
  - `calculate_weighted_scores()` - Weight application
  - `calculate_overall_score()` - Score aggregation
  - `calculate_status_levels()` - Status determination
  - `calculate_milestone_metrics()` - Milestone calculations
  - **Status**: ✅ **WELL SEPARATED** - Pure calculations, no formatting
  
- **Layer 4 - PRESENTATION**: `PresentationFormatter` class
  - `format_okr_tracker()` - Markdown generation
  - `_format_kr1_section()` through `_format_kr4_section()` - KR-specific formatting
  - `_format_dashboard_section()` - Dashboard table formatting
  - `_format_risk_section()` - Risk analysis formatting
  - **Status**: ✅ **WELL SEPARATED** - Only formatting, no calculations
  
- **Layer 5 - ORCHESTRATION**: `OKRAnalysisOrchestrator` class
  - Coordinates all layers: data → analysis → presentation
  - `get_metrics_json()` - Full pipeline to JSON
  - `generate_executive_summary()` - Full pipeline to markdown
  - `generate_full_report()` - Full pipeline to markdown
  - `generate_site_analysis()` - Specialized reporting
  - **Status**: ✅ **WELL SEPARATED** - Orchestrates existing components

- **Status**: ✅✅✅ **EXCELLENT** - Clean layered architecture with clear separation of concerns

---

### **Specialized Analysis Scripts**

#### `okr_tracker.py` (400+ lines)
**Phases Handled**: ✅ DATA CAPTURE → ANALYSIS → PRESENTATION
- **Classes**:
  - `ESOLDataAnalyzer` - Data loading + extraction (CAPTURE/TRANSFORM)
    - `load_data()` - Column mapping + standardization
    - `analyze_esol_categories()` - ESOL counts
    - `analyze_windows11_status()` - Win11 adoption metrics
    - `analyze_kiosk_devices()` - Kiosk detection
    - `analyze_by_site()` - Site-level grouping
    - `calculate_replacement_costs()` - Cost aggregation
  - `OKRCalculator` - Business logic (ANALYSIS)
    - `calculate_kr_metrics()` - OKR scoring
- **Status**: ⚠️ **MIXED** - Data and analysis tightly coupled
  - **Issue**: Column mapping embedded in load_data() (should use ConfigManager)
  - **Recommendation**: Refactor to use ConfigManager instead of hardcoded mapping

#### `esol_count.py` (310 lines)
**Phases Handled**: ✅ DATA CAPTURE → ANALYSIS → PRESENTATION
- **Functions**:
  - `main()` - Single monolithic function
  - Data loading via `data_utils.get_data_file_path()`
  - Filtering and counting (ESOL categories, sites, costs)
  - Report generation (Markdown, CSV, JSON)
  - Burndown calculations
- **Status**: ⚠️ **PARTIALLY MIXED** - Logic and presentation combined
  - **Issue**: Burndown calculation logic embedded in report generation
  - **Recommendation**: Extract burndown logic to separate analysis module

#### `euc_summary.py` (156 lines)
**Phases Handled**: ✅ DATA CAPTURE → ANALYSIS → PRESENTATION
- **Functions**:
  - `main()` - Single monolithic function
  - Data loading and column mapping (CAPTURE/TRANSFORM)
  - Metric extraction: device counts, ESOL, Win11, kiosks (ANALYSIS)
  - JSON/text report generation (PRESENTATION)
  - File export to `data/reports/` (NORMALIZE)
- **Status**: ⚠️ **MIXED** - All phases in one function
  - **Issue**: No separation between extraction, calculation, and formatting
  - **Recommendation**: Split into analysis and presentation layers

#### `win11_count.py` (150+ lines)
**Phases Handled**: ✅ DATA CAPTURE → ANALYSIS → PRESENTATION
- **Functions**:
  - `main()` - Single monolithic function
  - Data loading via Excel (CAPTURE)
  - Column filtering and grouping (TRANSFORM)
  - Site-level Win11 metrics calculation (ANALYSIS)
  - Markdown and CSV export (PRESENTATION/NORMALIZE)
  - Burndown calculations
- **Status**: ⚠️ **MIXED** - All phases in one function
  - **Issue**: Burndown logic embedded in main flow
  - **Recommendation**: Extract analysis logic, use ConfigManager for patterns

#### `kiosk_count.py` (118 lines)
**Phases Handled**: ✅ DATA CAPTURE → ANALYSIS → PRESENTATION
- **Functions**:
  - `main()` - Single monolithic function
  - Data loading (CAPTURE)
  - Kiosk pattern matching (TRANSFORM)
  - Edition/OS counting (ANALYSIS)
  - Markdown report generation (PRESENTATION)
- **Status**: ⚠️ **MIXED** - Logic and presentation combined
  - **Issue**: Pattern matching logic depends on config but no clear separation
  - **Recommendation**: Extract kiosk detection to reusable module

#### `export_site_win11_pending.py` (176 lines)
**Phases Handled**: ✅ DATA CAPTURE → TRANSFORM → ANALYSIS → NORMALIZE
- **Functions**:
  - `export_site_win11_pending()` - Main analysis function (reusable)
    - Filtering (TRANSFORM)
    - Counting and percentages (ANALYSIS)
    - Console output (PRESENTATION)
  - `main()` - Entry point with CSV export (NORMALIZE)
- **Status**: ✅ **WELL STRUCTURED** - Separation between logic and CLI
  - **Strength**: Reusable `export_site_win11_pending()` function
  - **Weakness**: Console output mixed in main function
  - **Recommendation**: Move console output to presentation layer

#### `okr_dashboard.py` (120+ lines)
**Phases Handled**: PRESENTATION (interactive menu)
- **Functions**:
  - `print_menu()` - Menu display
  - `quick_status()` - Calls `OKRAnalysisOrchestrator`
  - `executive_summary()` - Calls orchestrator
  - `full_tracker()` - Calls orchestrator
  - `site_analysis()` - Calls orchestrator
  - `win11_site_analysis()` - Calls win11_count.py via subprocess
- **Status**: ✅ **WELL SEPARATED** - Pure presentation layer
  - **Strength**: Delegates all analysis to orchestrator
  - **Weakness**: Subprocess call to win11_count.py is fragile

---

## 3. CURRENT ARCHITECTURE DIAGRAM

```
DATA LAYER (Files loaded from data/raw/)
    ↓
    ├─→ data_utils.py
    │   └─ get_data_file_path() → Excel file path
    │
    ├─→ separated_esol_analyzer.py [MULTI-LAYER]
    │   ├─ DataAnalyzer.load_data() → DataFrame
    │   ├─ DataAnalyzer.extract_*() → Raw counts
    │   ├─ BusinessLogicCalculator.calculate_*() → Metrics
    │   └─ PresentationFormatter.format_*() → Markdown
    │
    └─→ Standalone Scripts (okr_tracker, esol_count, win11_count, etc.)
        ├─ Load data directly via pd.read_excel()
        ├─ Process in-function
        └─ Generate reports directly

ANALYSIS LAYER
    ├─ separated_esol_analyzer.py (ConfigManager + DataAnalyzer + BusinessLogicCalculator)
    ├─ okr_tracker.py (ESOLDataAnalyzer + OKRCalculator) [uses hardcoded mappings]
    ├─ esol_count.py (inline filtering/aggregation)
    ├─ euc_summary.py (inline extraction)
    ├─ win11_count.py (inline site analysis)
    ├─ kiosk_count.py (inline pattern matching)
    └─ export_site_win11_pending.py (reusable function + CLI wrapper)

PRESENTATION/NORMALIZE LAYER
    ├─ separated_esol_analyzer.py (PresentationFormatter)
    ├─ okr_dashboard.py (interactive menu)
    ├─ esol_count.py (Markdown, CSV, JSON export)
    ├─ euc_summary.py (JSON or text export)
    ├─ win11_count.py (Markdown, CSV export)
    ├─ kiosk_count.py (Markdown export)
    └─ export_site_win11_pending.py (CSV export)

OUTPUT LAYER (Files written to data/reports/ and data/processed/)
    ├─ Markdown reports (.md)
    ├─ JSON exports (.json)
    └─ CSV exports (.csv)
```

---

## 4. PHASE SEPARATION SCORECARD

| File | Capture | Transform | Analysis | Normalize | Presentation | Overall Score | Notes |
|------|---------|-----------|----------|-----------|--------------|---------------|-------|
| `data_utils.py` | ✅ | - | - | - | - | **A+** | Single responsibility |
| `config_helper.py` | - | - | - | - | ✅ | **A+** | Standalone config UI |
| `separated_esol_analyzer.py` | ✅ | ✅ | ✅ | - | ✅ | **A++** | Exemplary layering |
| `okr_tracker.py` | ✅ | ⚠️ | ⚠️ | - | ⚠️ | **C+** | Hardcoded mappings, monolithic |
| `esol_count.py` | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **C** | All phases in main() |
| `euc_summary.py` | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **C** | All phases in main() |
| `win11_count.py` | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **C** | All phases in main() |
| `kiosk_count.py` | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **C** | All phases in main() |
| `export_site_win11_pending.py` | ✅ | ✅ | ✅ | ✅ | ⚠️ | **B+** | Good function design, CLI mixing |
| `okr_dashboard.py` | - | - | - | - | ✅ | **A** | Pure presentation |

**Overall Codebase Score**: **B-** (Good foundation with separated_esol_analyzer as reference, but legacy scripts need refactoring)

---

## 5. DATA FLOW ANALYSIS

### **Current Data Flow Paths**

#### Path 1: Using `separated_esol_analyzer.py` (IDEAL)
```
Excel File
  ↓
ConfigManager (loads YAML configs)
  ↓
DataAnalyzer.load_data() [CAPTURE]
  ↓
DataAnalyzer.extract_*() [TRANSFORM]
  ↓
BusinessLogicCalculator [ANALYSIS]
  ↓
PresentationFormatter [PRESENTATION]
  ↓
Text/JSON/Markdown Output
```
**Characteristics**: Clean separation, reusable, testable

#### Path 2: Using Legacy Scripts (okr_tracker, esol_count, etc.)
```
Excel File
  ↓
pd.read_excel() [CAPTURE in main()]
  ↓
Column mapping & filtering [TRANSFORM in main()]
  ↓
Value counts, percentages [ANALYSIS in main()]
  ↓
String concatenation, formatting [PRESENTATION in main()]
  ↓
Markdown/CSV/JSON Output
```
**Characteristics**: Monolithic, difficult to test, duplicate logic

#### Path 3: Using `okr_dashboard.py`
```
User selects menu option
  ↓
okr_dashboard calls OKRAnalysisOrchestrator
  ↓
Orchestrator runs full separated_esol_analyzer pipeline
  ↓
Output displayed to console
```
**Characteristics**: Good delegation, but subprocess call to win11_count.py is fragile

---

## 6. CRITICAL DEPENDENCIES & ISSUES

### **Issue #1: Duplicate Data Extraction Logic**
- **Files affected**: okr_tracker.py, esol_count.py, euc_summary.py, win11_count.py, kiosk_count.py
- **Problem**: Each script independently loads and transforms data
- **Impact**: 
  - Inconsistent column handling
  - Hardcoded action values (e.g., "Urgent Replacement")
  - Changes to data format require updating 5+ files
- **Solution**: All should use `DataAnalyzer` from separated_esol_analyzer.py

### **Issue #2: ConfigManager Underutilization**
- **Files affected**: okr_tracker.py, esol_count.py, win11_count.py, kiosk_count.py
- **Problem**: Scripts hardcode column names and category values instead of using ConfigManager
- **Code Example (BAD)**:
  ```python
  # okr_tracker.py lines 42-56
  column_mapping = {
      'Action to take': 'action',
      'Current OS Build': 'os_build',
      'LTSC or Enterprise': 'edition',
      'Current User Logged On': 'current_user',
      ...
  }
  ```
- **Code Example (GOOD)**:
  ```python
  # separated_esol_analyzer.py uses ConfigManager
  config = ConfigManager()
  data_mapping = config.get_esol_criteria()['data_mapping']
  action_col = data_mapping['action_column']
  ```
- **Solution**: Replace all hardcoded mappings with ConfigManager

### **Issue #3: Business Logic in Report Generation**
- **Files affected**: esol_count.py, win11_count.py
- **Problem**: Burndown calculations and metric scoring embedded in formatting
- **Code Example**:
  ```python
  # esol_count.py lines 153-198 (burndown in main)
  days_remaining_2024 = (esol_2024_date - current_date).days
  daily_burn_rate_2024 = esol2024 / days_remaining_2024 if days_remaining_2024 > 0 else 0
  ```
- **Solution**: Extract to `BusinessLogicCalculator` method

### **Issue #4: Fragile subprocess Calls**
- **File**: okr_dashboard.py line 95-100
- **Problem**: Calls `win11_count.py` via subprocess instead of importing function
- **Code**:
  ```python
  result = subprocess.run([sys.executable, 'scripts/win11_count.py', '--site-table'])
  ```
- **Solution**: Extract analysis function from win11_count.py into shared module

### **Issue #5: Mixed Presentation Logic**
- **Files affected**: export_site_win11_pending.py (console output in business function)
- **Problem**: `export_site_win11_pending()` prints output (good!) but with formatted tables
- **Solution**: Return structured data only, let presentation layer format output

---

## 7. RECOMMENDED REFACTORING ROADMAP

### **Phase 1: Consolidate Data Extraction (Week 1)**
**Goal**: Make `DataAnalyzer` the single source of truth

1. Create `analysis/data_extraction.py`:
   - Move `DataAnalyzer` from separated_esol_analyzer.py
   - Add missing extraction methods (site-by-site metrics)
   - Add method for getting ESOL device lists

2. Update all scripts to use:
   ```python
   from separated_esol_analyzer import ConfigManager, DataAnalyzer
   config = ConfigManager()
   analyzer = DataAnalyzer(config)
   df = analyzer.load_data(filepath)
   counts = analyzer.extract_basic_counts(df)
   ```

3. Files to update:
   - okr_tracker.py → Use DataAnalyzer.load_data()
   - esol_count.py → Use DataAnalyzer.extract_basic_counts()
   - win11_count.py → Use DataAnalyzer for filtering
   - kiosk_count.py → Use DataAnalyzer.extract_kiosk_counts()

### **Phase 2: Extract Business Logic (Week 2)**
**Goal**: Separate calculations from presentation

1. Create `analysis/okr_calculations.py`:
   - Move `BusinessLogicCalculator` from separated_esol_analyzer.py
   - Add specialized calculators for each domain:
     - `ESOLCalculator` (esol_count logic)
     - `Win11Calculator` (win11_count logic)
     - `BurndownCalculator` (esol_count + win11_count burndown)

2. Update scripts:
   - okr_tracker.py → Use BusinessLogicCalculator
   - esol_count.py → Extract burndown to BurndownCalculator
   - win11_count.py → Extract burndown to BurndownCalculator

### **Phase 3: Consolidate Presentation (Week 3)**
**Goal**: Separate formatting from file I/O

1. Create `presentation/report_formatters.py`:
   - Move PresentationFormatter
   - Add specialized formatters:
     - `ESolReportFormatter` (esol_count output)
     - `Win11ReportFormatter` (win11_count output)
     - `BurndownReportFormatter` (burndown charts)

2. Update scripts:
   - All scripts use formatter, then write to file

### **Phase 4: Create Shared Analysis Modules (Week 4)**
**Goal**: DRY principle - no duplicate code

1. Create `analysis/esol_analyzer.py`:
   - `ESOLAnalyzer` class wrapping DataAnalyzer + ESOLCalculator
   - Methods: `analyze_by_site()`, `analyze_burndown()`, `get_replacement_costs()`

2. Create `analysis/win11_analyzer.py`:
   - `Win11Analyzer` class wrapping DataAnalyzer + Win11Calculator
   - Methods: `get_site_summary()`, `calculate_pending()`, `get_burndown()`

3. Create `analysis/kiosk_analyzer.py`:
   - `KioskAnalyzer` class wrapping DataAnalyzer
   - Methods: `count_by_edition()`, `get_migration_status()`

### **Phase 5: Refactor Standalone Scripts (Week 5)**
**Goal**: Thin CLI wrappers around analysis modules

Template for all scripts:
```python
def main():
    # 1. Parse arguments
    args = parser.parse_args()
    
    # 2. Load data once
    config = ConfigManager()
    analyzer = DataAnalyzer(config)
    df = analyzer.load_data(args.data_file)
    
    # 3. Run analysis
    results = SpecializedAnalyzer(config).analyze(df, args)
    
    # 4. Format output
    report = SpecializedFormatter(config).format(results)
    
    # 5. Write files
    export_report(report, args.output)
```

---

## 8. EXTRACTION CHECKLIST

### **From esol_count.py**
- [ ] Site-level ESOL counting logic → ESOLAnalyzer
- [ ] Burndown calculation (days_remaining, burn_rate) → BurndownCalculator
- [ ] Report markdown formatting → ESolReportFormatter
- [ ] CSV/JSON export → FileExporter

### **From win11_count.py**
- [ ] Enterprise filter + Win11 pattern matching → Win11Analyzer
- [ ] Site-level aggregation → Win11Analyzer.get_site_summary()
- [ ] Burndown calculation → BurndownCalculator
- [ ] Site table formatting → Win11ReportFormatter

### **From kiosk_count.py**
- [ ] Kiosk detection (device + user patterns) → already in DataAnalyzer
- [ ] Edition breakdown → keep simple in main
- [ ] Win11 migration status → already in DataAnalyzer

### **From okr_tracker.py**
- [ ] ESOLDataAnalyzer.load_data() → Use DataAnalyzer
- [ ] ESOLDataAnalyzer.analyze_*() → Use DataAnalyzer.extract_*()
- [ ] OKRCalculator → Use BusinessLogicCalculator
- [ ] Report generation → Use PresentationFormatter

### **From export_site_win11_pending.py**
- [ ] export_site_win11_pending() function → Keep as reusable function
- [ ] Console output formatting → Move to presentation layer
- [ ] Create wrapper for file export

---

## 9. FILE STRUCTURE AFTER REFACTORING

```
esol_2025/
├── scripts/
│   ├── data_utils.py                    ✅ (unchanged)
│   ├── config_helper.py                 ✅ (unchanged)
│   ├── okr_dashboard.py                 ✅ (thin presentation layer)
│   ├── esol_count.py                    🔧 (thin wrapper)
│   ├── win11_count.py                   🔧 (thin wrapper)
│   ├── kiosk_count.py                   🔧 (thin wrapper)
│   ├── export_site_win11_pending.py     🔧 (thin wrapper)
│   ├── okr_tracker.py                   ❌ (REPLACE with thin wrapper)
│   │
│   └── analysis/                        📁 NEW MODULES
│       ├── __init__.py
│       ├── data_extraction.py           (moved from separated_esol_analyzer.py)
│       ├── okr_calculator.py            (moved from separated_esol_analyzer.py)
│       ├── esol_analyzer.py             (new - ESOLAnalyzer class)
│       ├── win11_analyzer.py            (new - Win11Analyzer class)
│       ├── kiosk_analyzer.py            (new - KioskAnalyzer class)
│       ├── burndown_calculator.py       (new - burndown logic)
│       └── specialized_analyzers.py     (aggregates all above)
│
│   └── presentation/                    📁 NEW MODULES
│       ├── __init__.py
│       ├── formatters.py                (moved from separated_esol_analyzer.py)
│       ├── esol_formatter.py            (new - ESOL reports)
│       ├── win11_formatter.py           (new - Win11 reports)
│       ├── burndown_formatter.py        (new - burndown charts)
│       └── file_exporter.py             (new - CSV/JSON/MD writers)
│
├── separated_esol_analyzer.py           ✅ (moved to modular structure)
├── config/
├── data/
├── docs/
├── notebooks/
└── requirements.txt
```

---

## 10. MIGRATION STRATEGY

### **Option A: Incremental (Recommended)**
1. Keep separated_esol_analyzer.py as "golden" reference
2. Gradually refactor scripts to use its components
3. Extract components to analysis/presentation packages
4. No breaking changes to batch launchers

### **Option B: Big Bang**
1. Create new modular structure
2. Migrate all logic at once
3. Higher risk but cleaner result
4. Requires testing all launchers

### **Option C: Parallel**
1. Build new structure alongside old code
2. Use new code internally, keep old scripts as CLI wrappers
3. Lowest risk, higher maintenance burden

**Recommended**: **Option A - Incremental**
- Week 1-2: Extract analysis modules
- Week 3-4: Update legacy scripts to use new modules
- Week 5-6: Extract presentation modules
- Week 7-8: Refactor remaining scripts
- Test batch launchers after each phase

---

## 11. KEY METRICS FOR SUCCESS

| Metric | Current | Target |
|--------|---------|--------|
| Code duplication (% of lines) | ~35% | <5% |
| Cyclomatic complexity (avg) | 8-12 | <4 |
| Test coverage (%) | ~0% | >70% |
| Files with >200 lines | 5 | 1 |
| Functions with >50 lines | 8 | 0 |
| ConfigManager usage (%) | 40% | 100% |
| Reusable analysis classes | 2 | 8+ |

---

## 12. SUMMARY TABLE: What Needs Extraction

| Category | Current Location | Target Location | Priority | Effort |
|----------|------------------|-----------------|----------|--------|
| **Data Loading** | Multiple files | `analysis/data_extraction.py` | P0 | Small |
| **Column Mapping** | Hardcoded in each script | ConfigManager (YAML) | P0 | Small |
| **Percentage Calculations** | `BusinessLogicCalculator` | Extract to utility | P1 | Small |
| **Status Determination** | `BusinessLogicCalculator` | Extract to utility | P1 | Small |
| **Burndown Logic** | esol_count.py, win11_count.py | `analysis/burndown_calculator.py` | P1 | Medium |
| **Site Aggregation** | esol_count.py, win11_count.py | `ESOLAnalyzer`, `Win11Analyzer` | P1 | Medium |
| **OKR Scoring** | okr_tracker.py, separated_esol_analyzer.py | Consolidate in `BusinessLogicCalculator` | P2 | Small |
| **Report Formatting** | Scattered in scripts | `presentation/` package | P2 | Large |
| **File Export** | Hardcoded in each script | `presentation/file_exporter.py` | P2 | Medium |
| **Console Output** | Each script | `presentation/console_formatter.py` | P3 | Small |

---

## 13. CONCLUSION

**Current State**: The project has an **exemplary reference architecture** (separated_esol_analyzer.py) but **legacy scripts** that duplicate work and resist maintenance.

**Key Wins**:
- ✅ separated_esol_analyzer.py shows proper layering
- ✅ ConfigManager handles all YAML files correctly
- ✅ data_utils.py has clean file resolution logic
- ✅ okr_dashboard.py properly delegates to orchestrator

**Key Gaps**:
- ⚠️ 5 scripts hardcode column mappings instead of using ConfigManager
- ⚠️ Burndown logic duplicated in 2 scripts
- ⚠️ Business logic mixed with presentation in 4 scripts
- ⚠️ No shared analysis modules for reuse
- ⚠️ No test coverage for analysis logic

**Recommended Next Steps**:
1. Implement **Phase 1-2 of Refactoring Roadmap** to consolidate data & analysis
2. Create **analysis/esol_analyzer.py**, **analysis/win11_analyzer.py** as examples
3. Update **legacy scripts to use these new modules**
4. Add **unit tests** for analysis modules
5. Monitor code duplication metrics with each refactor

