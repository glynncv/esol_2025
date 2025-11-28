# ESOL ETL Architecture: Current vs Recommended

## Quick Visual Summary

### CURRENT ARCHITECTURE (B- Grade)

```
LEGACY APPROACH: Monolithic Scripts
=====================================

esol_count.py          win11_count.py         kiosk_count.py
    |                      |                      |
    +--[Load Excel]         +--[Load Excel]        +--[Load Excel]
    |   [Filter]            |   [Filter]           |   [Filter]
    |   [Count]             |   [Count]            |   [Count]
    |   [Calculate %]        |   [Calculate %]      |   [Calculate %]
    |   [Format MD]         |   [Format MD]        |   [Format MD]
    |   [Export CSV]        |   [Export CSV]       |   [Export CSV]
    |                       |                      |
    v                       v                      v
  Reports                Reports                 Reports
  (duplicated logic in each)

separated_esol_analyzer.py (THE GOOD EXAMPLE)
==============================================

    ConfigManager ─── [Load YAML configs]
           |
    DataAnalyzer ────────── [Extract raw counts] ✅ CLEAN
           |
    BusinessLogicCalculator [Calculate metrics]  ✅ CLEAN
           |
    PresentationFormatter ── [Format output]     ✅ CLEAN
           |
    OKRAnalysisOrchestrator [Coordinate layers]  ✅ CLEAN
           |
        Report
```

### RECOMMENDED ARCHITECTURE (A+ Grade)

```
MODULAR APPROACH: Clean Separation of Concerns
===============================================

DATA LAYER:
    ConfigManager ──── config/*.yaml files
           |
    data_utils.py ───── file path resolution
           |
    DataAnalyzer ────── Excel → DataFrame [NO LOGIC]


ANALYSIS LAYER (NEW):
    ESOLAnalyzer ─────────── esol domain logic
    Win11Analyzer ────────── win11 domain logic
    KioskAnalyzer ────────── kiosk domain logic
    BurndownCalculator ───── timeline metrics
    BusinessLogicCalculator  okr scoring


PRESENTATION LAYER (NEW):
    ESolFormatter ────────── esol reports
    Win11Formatter ────────── win11 reports
    BurndownFormatter ──────── burndown charts
    FileExporter ─────────── CSV/JSON/MD writers


SCRIPT LAYER (THIN WRAPPERS):
    esol_count.py ────────────┐
    win11_count.py ───────────┼─→ [Parse args → Load data → Run analyzer → Format → Export]
    kiosk_count.py ───────────┤
    export_site_win11_pending ┤
    okr_dashboard.py ─────────┘
```

## File-by-File Transformation

### TIER 1: Perfect (No changes needed)
```
✅ data_utils.py          [A+] Single responsibility: file resolution
✅ config_helper.py       [A+] Configuration UI only
✅ okr_dashboard.py       [A]  Thin presentation layer
✅ separated_esol_analyzer.py [A++] Reference architecture (keep as template)
```

### TIER 2: Good Structure, Minor Improvements
```
🔧 export_site_win11_pending.py [B+]
   Current: Reusable function + CLI
   Action:  Move console output to presentation layer
   Impact:  +5 lines (presentation wrapper)
```

### TIER 3: Needs Refactoring
```
⚠️ okr_tracker.py [C+]
   Problems:
     • Hardcoded column mapping (should use ConfigManager)
     • ESOLDataAnalyzer duplicates DataAnalyzer
     • OKRCalculator logic should be in BusinessLogicCalculator
   Solution: Use DataAnalyzer + BusinessLogicCalculator from separated_esol_analyzer.py
   Lines to remove: ~150 (duplicate extraction)
   
⚠️ esol_count.py [C]
   Problems:
     • All phases in main() function
     • Burndown logic embedded in report generation
     • Hardcoded action values
   Solution: Extract to ESOLAnalyzer + BurndownCalculator
   Lines to remove: ~180 (logic) → becomes: ~40 (thin wrapper)

⚠️ win11_count.py [C]
   Problems:
     • All phases in main() function
     • Burndown logic embedded in report generation
     • Site aggregation duplicated
   Solution: Extract to Win11Analyzer + BurndownCalculator
   Lines to remove: ~140 (logic) → becomes: ~35 (thin wrapper)

⚠️ kiosk_count.py [C]
   Problems:
     • Monolithic main() function
     • Duplicate pattern matching logic
   Solution: Use DataAnalyzer.extract_kiosk_counts()
   Lines to remove: ~50 (logic) → becomes: ~25 (thin wrapper)

⚠️ euc_summary.py [C]
   Problems:
     • All phases in main() function
     • No separation between extraction, calculation, formatting
   Solution: Use DataAnalyzer + BusinessLogicCalculator
   Lines to remove: ~120 (logic) → becomes: ~30 (thin wrapper)
```

## Comparison: Lines of Code

### BEFORE Refactoring
```
okr_tracker.py ..................... 400+ lines
esol_count.py ....................... 310 lines
separated_esol_analyzer.py ......... 1000+ lines  (but exemplary!)
euc_summary.py ....................... 156 lines
win11_count.py ....................... 150+ lines
export_site_win11_pending.py ......... 176 lines
kiosk_count.py ....................... 118 lines
okr_dashboard.py ..................... 120+ lines
data_utils.py ......................... 94 lines
config_helper.py ..................... 192 lines
─────────────────────────────────────────────────
TOTAL ............................... ~2650 lines
Avg function size .................... ~40 lines
Code duplication ..................... ~35%
```

### AFTER Refactoring (Target)
```
scripts/
├── data_utils.py ....................... 94 lines  (unchanged)
├── config_helper.py ................... 192 lines  (unchanged)
├── okr_dashboard.py ................... 120 lines  (unchanged)
├── esol_count.py ........................ 40 lines  (THIN WRAPPER)
├── win11_count.py ....................... 35 lines  (THIN WRAPPER)
├── kiosk_count.py ....................... 25 lines  (THIN WRAPPER)
├── export_site_win11_pending.py ......... 50 lines  (thin wrapper)
├── okr_tracker.py ....................... 45 lines  (thin wrapper or REMOVED)
│
├── analysis/
│   ├── __init__.py ......................... 2 lines
│   ├── data_extraction.py ............... 250 lines  (moved from separated_esol_analyzer.py)
│   ├── okr_calculator.py ............... 180 lines  (moved from separated_esol_analyzer.py)
│   ├── esol_analyzer.py ................. 80 lines  (new - domain logic)
│   ├── win11_analyzer.py ................. 90 lines  (new - domain logic)
│   ├── kiosk_analyzer.py ................. 40 lines  (new - domain logic)
│   └── burndown_calculator.py ........... 70 lines  (extracted - shared logic)
│
└── presentation/
    ├── __init__.py ......................... 2 lines
    ├── formatters.py .................... 400 lines  (moved from separated_esol_analyzer.py)
    ├── esol_formatter.py ................ 100 lines  (new - domain formatter)
    ├── win11_formatter.py ............... 100 lines  (new - domain formatter)
    ├── burndown_formatter.py ............ 80 lines  (new - shared formatter)
    └── file_exporter.py ................. 60 lines  (new - CSV/JSON writers)
─────────────────────────────────────────────────
TOTAL ............................... ~2550 lines
Avg function size ...................... ~20 lines
Code duplication ....................... <5%

NET CHANGE: -100 lines, but 40% less duplication!
```

## Key Metrics Improvement Path

| Metric | Current | After Phase 1 | After Phase 2 | After Phase 3 | Target |
|--------|---------|--------------|--------------|--------------|--------|
| **Code duplication (%)** | 35 | 28 | 15 | 5 | <5 |
| **Avg function size** | 40 | 35 | 25 | 18 | <20 |
| **Cyclomatic complexity** | 8-12 | 6-10 | 4-8 | 3-6 | <4 |
| **Test coverage (%)** | 0 | 0 | 25 | 60 | >70 |
| **ConfigManager usage (%)** | 40 | 60 | 80 | 100 | 100 |
| **Reusable classes** | 2 | 4 | 7 | 10 | 8+ |

## Phase-by-Phase Impact

### Phase 1: Data Extraction Consolidation
```
BEFORE:
├─ okr_tracker.py uses ESOLDataAnalyzer [hardcoded]
├─ esol_count.py uses inline pd.read_excel()
├─ win11_count.py uses inline pd.read_excel()
├─ kiosk_count.py uses inline pd.read_excel()
└─ euc_summary.py uses inline pd.read_excel()

AFTER:
├─ okr_tracker.py uses DataAnalyzer [configured]
├─ esol_count.py uses DataAnalyzer
├─ win11_count.py uses DataAnalyzer
├─ kiosk_count.py uses DataAnalyzer
└─ euc_summary.py uses DataAnalyzer

Result: Single source of truth, consistent column handling
Impact: 4-6 hours, 150 lines removed from legacy scripts
```

### Phase 2: Business Logic Extraction
```
BEFORE:
└─ Calculations scattered in okr_tracker, esol_count, win11_count

AFTER:
├─ BusinessLogicCalculator [okr scoring, percentages]
├─ ESOLCalculator [domain-specific]
├─ Win11Calculator [domain-specific]
└─ BurndownCalculator [shared]

Result: Calculations reusable, testable, documented
Impact: 6-8 hours, 200 lines removed from legacy scripts
```

### Phase 3: Presentation Consolidation
```
BEFORE:
├─ esol_count.py formats Markdown directly [80 lines]
├─ win11_count.py formats Markdown directly [70 lines]
├─ kiosk_count.py formats Markdown directly [40 lines]
└─ export_site_win11_pending.py prints to console [50 lines]

AFTER:
├─ ESolFormatter [80 lines] ─→ Markdown
├─ Win11Formatter [70 lines] ─→ Markdown
├─ BurndownFormatter [60 lines] ─→ Markdown
└─ FileExporter [60 lines] ─→ CSV/JSON writers

Result: Consistent formatting, easy to theme, reusable
Impact: 8-10 hours, 240 lines removed from legacy scripts
```

### Phase 4: Domain Analyzer Integration
```
BEFORE:
└─ Each script loads, analyzes, formats independently

AFTER:
├─ esol_count.py: Load → ESOLAnalyzer.analyze() → ESolFormatter → FileExporter
├─ win11_count.py: Load → Win11Analyzer.analyze() → Win11Formatter → FileExporter
├─ kiosk_count.py: Load → DataAnalyzer → format → FileExporter
└─ export_site_win11_pending.py: Load → Win11Analyzer → FileExporter

Result: Thin CLI wrappers, easy to test individual components
Impact: 6-8 hours, 300 lines removed from legacy scripts
```

## Testing Strategy

### BEFORE
```
No tests (0% coverage)
Hard to test due to mixed concerns
```

### AFTER
```
analysis/test_data_extraction.py
├─ test_load_data()
├─ test_extract_basic_counts()
├─ test_extract_kiosk_counts()
└─ test_validate_columns()

analysis/test_calculators.py
├─ test_calculate_percentages()
├─ test_calculate_kr_scores()
├─ test_calculate_status_levels()
└─ test_burndown_rates()

analysis/test_domain_analyzers.py
├─ test_esol_analyzer()
├─ test_win11_analyzer()
└─ test_kiosk_analyzer()

presentation/test_formatters.py
├─ test_esol_formatter()
├─ test_win11_formatter()
└─ test_burndown_formatter()

Integration tests (use real sample data)
├─ test_esol_count_workflow()
├─ test_win11_count_workflow()
└─ test_okr_dashboard_workflow()
```

## Risk Assessment

### LOW RISK Changes
- Extract ConfigManager usage (already done in separated_esol_analyzer.py)
- Move DataAnalyzer to separate module (it's already isolated)
- Extract formatters from presentation (simple string builders)
- Create thin CLI wrappers (minimal logic)

### MEDIUM RISK Changes
- Consolidate BusinessLogicCalculator logic (ensure all formulas preserved)
- Extract BurndownCalculator (test against existing outputs)
- Update okr_dashboard.py subprocess calls (test with all features)

### HIGH RISK Changes
- Removing okr_tracker.py (ensure okr_dashboard works as replacement)
- Changing column mapping sources (extensive testing required)
- Refactoring data filtering logic (validate against historical outputs)

## Success Criteria

1. All test files pass (>70% coverage)
2. All batch launchers work identically
3. Code duplication drops below 5%
4. Average function size < 20 lines
5. All scripts use ConfigManager for column mapping
6. No breaking changes to output format

