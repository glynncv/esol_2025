# Manual Testing Plan for ETL Restructuring

This document provides step-by-step manual testing procedures to verify the ETL restructuring works correctly in practice.

## Prerequisites

- Python 3.8+ installed
- Dependencies installed: `pip install -r requirements.txt`
- Test data file: `data/raw/EUC_ESOL.xlsx` (or set `EUC_DATA_FILE` environment variable)

---

## Test Suite 1: Basic Script Execution

### Test 1.1: ESOL Analysis - Basic Run
**Objective**: Verify ESOL analysis script runs without errors

**Steps**:
1. Open terminal in project root
2. Run: `python scripts/esol_count.py`
3. **Expected**: 
   - Script executes without errors
   - Console output shows ESOL device counts
   - Report file created in `data/reports/` with name like `ESOL_Count_all_YYYYMMDD_HHMMSS.md`

**Verify**:
- [ ] No Python errors or exceptions
- [ ] Console output is formatted correctly
- [ ] Report file is created
- [ ] Report contains expected sections (counts, percentages)

**If fails**: Check error message, verify data file exists, check file permissions

---

### Test 1.2: ESOL Analysis - Category Filtering
**Objective**: Verify category filtering works

**Steps**:
1. Run: `python scripts/esol_count.py --category esol_2024`
2. Run: `python scripts/esol_count.py --category esol_2025`
3. Run: `python scripts/esol_count.py --category esol_2026`

**Expected**:
- Each run shows only the specified category
- Counts differ between categories
- Reports are generated for each category

**Verify**:
- [ ] Each category filter works correctly
- [ ] Output matches expected category
- [ ] No cross-category contamination

---

### Test 1.3: ESOL Analysis - Site Table
**Objective**: Verify site-level analysis works

**Steps**:
1. Run: `python scripts/esol_count.py --site-table`

**Expected**:
- Console shows site-level breakdown table
- CSV and JSON files created in `data/processed/`
- Files named like `esol_site_summary_YYYYMMDD_HHMMSS.csv`

**Verify**:
- [ ] Site table displays correctly in console
- [ ] CSV file is readable in Excel
- [ ] JSON file is valid JSON
- [ ] Site data matches console output

---

### Test 1.4: ESOL Analysis - Burndown
**Objective**: Verify burndown calculations work

**Steps**:
1. Run: `python scripts/esol_count.py --burndown`

**Expected**:
- Console shows burndown metrics for all ESOL categories
- Burndown report created in `data/reports/`
- Shows days remaining, daily burn rate, status (ON TRACK/AT RISK)

**Verify**:
- [ ] Burndown calculations appear correct
- [ ] Dates are formatted correctly
- [ ] Status indicators are accurate
- [ ] Report file is generated

---

### Test 1.5: ESOL Analysis - Combined Options
**Objective**: Verify multiple options work together

**Steps**:
1. Run: `python scripts/esol_count.py --site-table --burndown`

**Expected**:
- Both site table and burndown analysis are displayed
- Multiple report files are generated
- All outputs are correct

**Verify**:
- [ ] Both features work simultaneously
- [ ] No conflicts between options
- [ ] All reports are generated

---

## Test Suite 2: Windows 11 Analysis

### Test 2.1: Win11 Analysis - Basic Run
**Objective**: Verify Windows 11 analysis script runs

**Steps**:
1. Run: `python scripts/win11_count.py`

**Expected**:
- Script executes without errors
- Console shows Windows 11 eligible/upgraded/pending counts
- Report file created in `data/reports/`

**Verify**:
- [ ] No errors
- [ ] KPI metrics displayed (eligible, upgraded %, pending)
- [ ] Report file generated
- [ ] Numbers are reasonable (eligible >= upgraded)

---

### Test 2.2: Win11 Analysis - Site Table
**Objective**: Verify site-level Windows 11 analysis


**Steps**:
1. Run: `python scripts/win11_count.py --site-table`

**Expected**:
- Site-level Windows 11 breakdown table
- CSV and JSON exports created
- Data shows progress by site

**Verify**:
- [ ] Site table displays correctly
- [ ] Exports are valid
- [ ] Data matches console output

---

### Test 2.3: Win11 Analysis - Burndown
**Objective**: Verify Windows 11 burndown calculations

**Steps**:
1. Run: `python scripts/win11_count.py --burndown`

**Expected**:
- Burndown metrics for Windows 11 upgrade target (Oct 31, 2025)
- Daily burn rate needed
- KPI status (ON TRACK/AT RISK)
- Burndown report file

**Verify**:
- [ ] Target date is Oct 31, 2025
- [ ] Burn rate calculation is correct
- [ ] Status reflects current progress
- [ ] Report file generated

---

### Test 2.4: Win11 Analysis - Combined Options
**Objective**: Verify multiple Win11 options work together

**Steps**:
1. Run: `python scripts/win11_count.py --site-table --burndown`

**Expected**:
- Both site table and burndown displayed
- Multiple reports generated
- All outputs correct

**Verify**:
- [ ] Both features work together
- [ ] No conflicts
- [ ] All reports generated

---

## Test Suite 3: Kiosk Analysis

### Test 3.1: Kiosk Analysis - Basic Run
**Objective**: Verify kiosk analysis script runs

**Steps**:
1. Run: `python scripts/kiosk_count.py`

**Expected**:
- Script executes without errors
- Console shows kiosk device counts
- Enterprise vs LTSC breakdown
- Windows 11 migration status for LTSC kiosks
- Report file generated

**Verify**:
- [ ] No errors
- [ ] Kiosk detection works (devices identified correctly)
- [ ] Enterprise/LTSC breakdown is accurate
- [ ] Report file generated

---

## Test Suite 4: Data Consistency Checks

### Test 4.1: Cross-Script Validation
**Objective**: Verify data consistency across scripts

**Steps**:
1. Run all three scripts and note total device counts:
   - `python scripts/esol_count.py` → Note total devices
   - `python scripts/win11_count.py` → Note total enterprise devices
   - `python scripts/kiosk_count.py` → Note total devices

**Expected**:
- Total devices should match across scripts (or be explainable)
- Enterprise device counts should be consistent
- No data loading errors

**Verify**:
- [ ] Total device counts are consistent
- [ ] Enterprise counts match between Win11 and Kiosk scripts
- [ ] No unexplained discrepancies

---

### Test 4.2: Filter Logic Verification
**Objective**: Verify filtering logic is correct

**Steps**:
1. Run ESOL analysis and note ESOL 2024 count
2. Run Win11 analysis and verify ESOL devices are excluded from eligible count
3. Check that Enterprise filter excludes LTSC correctly

**Expected**:
- ESOL devices excluded from Win11 eligible count
- Enterprise filter works correctly
- No double-counting or missing devices

**Verify**:
- [ ] ESOL exclusion works in Win11 analysis
- [ ] Enterprise filter excludes LTSC
- [ ] Filtering logic is consistent

---

## Test Suite 5: Output Format Verification

### Test 5.1: Markdown Report Format
**Objective**: Verify markdown reports are well-formatted

**Steps**:
1. Generate reports from all scripts
2. Open markdown files in a markdown viewer or GitHub

**Expected**:
- Reports are valid markdown
- Headers are properly formatted
- Tables render correctly
- Code blocks are formatted
- No broken formatting

**Verify**:
- [ ] Reports render correctly in markdown viewer
- [ ] Headers are hierarchical (H1, H2, H3)
- [ ] Tables are readable
- [ ] No markdown syntax errors

---

### Test 5.2: CSV Export Format
**Objective**: Verify CSV exports are valid

**Steps**:
1. Generate site tables from ESOL and Win11 scripts
2. Open CSV files in Excel or text editor

**Expected**:
- CSV files are valid
- Headers are present
- Data rows are correct
- No encoding issues
- Excel can open files without errors

**Verify**:
- [ ] CSV files open in Excel
- [ ] Headers are correct
- [ ] Data matches console output
- [ ] No encoding problems (special characters display correctly)

---

### Test 5.3: JSON Export Format
**Objective**: Verify JSON exports are valid

**Steps**:
1. Generate site tables from ESOL and Win11 scripts
2. Validate JSON files

**Expected**:
- JSON files are valid JSON
- Can be parsed by Python/json tools
- Structure is consistent

**Verify**:
- [ ] JSON files are valid (use `python -m json.tool <file.json>`)
- [ ] Structure is logical
- [ ] Data matches CSV/console output

---

## Test Suite 6: Error Handling

### Test 6.1: Missing Data File
**Objective**: Verify graceful error handling

**Steps**:
1. Temporarily rename or move `data/raw/EUC_ESOL.xlsx`
2. Run: `python scripts/esol_count.py`
3. Restore the file

**Expected**:
- Clear error message about missing file
- No Python traceback/crash
- Helpful guidance on how to fix

**Verify**:
- [ ] Error message is user-friendly
- [ ] Script exits gracefully
- [ ] No stack trace shown to user

---

### Test 6.2: Invalid Arguments
**Objective**: Verify argument validation

**Steps**:
1. Run: `python scripts/esol_count.py --category invalid_category`
2. Run: `python scripts/esol_count.py --invalid-option`

**Expected**:
- Clear error message about invalid arguments
- Help text displayed when appropriate
- Script exits gracefully

**Verify**:
- [ ] Invalid arguments are caught
- [ ] Error messages are helpful
- [ ] Help text is displayed for `--help`

---

### Test 6.3: Empty Data File
**Objective**: Verify handling of edge cases

**Steps**:
1. Create an empty Excel file (or file with no data rows)
2. Run analysis scripts
3. Restore original file

**Expected**:
- Scripts handle empty data gracefully
- Appropriate error messages or zero counts displayed
- No crashes

**Verify**:
- [ ] Empty data is handled correctly
- [ ] No division by zero errors
- [ ] Appropriate messages displayed

---

## Test Suite 7: Performance Testing

### Test 7.1: Execution Time
**Objective**: Verify scripts run in reasonable time

**Steps**:
1. Time each script execution:
   - `time python scripts/esol_count.py`
   - `time python scripts/win11_count.py`
   - `time python scripts/kiosk_count.py`

**Expected**:
- Scripts complete in < 30 seconds for typical data sizes
- No significant performance regression from restructuring

**Verify**:
- [ ] Execution time is acceptable
- [ ] No significant slowdowns
- [ ] Memory usage is reasonable

---

## Test Suite 8: Integration with Batch Files

### Test 8.1: Analyze.bat Integration
**Objective**: Verify batch file launchers work

**Steps**:
1. Run: `.\analyze.bat esol`
2. Run: `.\analyze.bat win11 --site-table`
3. Run: `.\analyze.bat kiosk`

**Expected**:
- Batch files execute Python scripts correctly
- Arguments are passed through
- Output is correct

**Verify**:
- [ ] Batch files work
- [ ] Arguments are passed correctly
- [ ] Output matches direct Python execution

---

### Test 8.2: Dashboard Integration
**Objective**: Verify dashboard uses ETL modules correctly

**Steps**:
1. Run: `python scripts/okr_dashboard.py`
2. Select various menu options
3. Verify reports are generated

**Expected**:
- Dashboard works correctly
- Uses ETL modules internally
- Reports are generated correctly

**Verify**:
- [ ] Dashboard menu works
- [ ] All options execute successfully
- [ ] Reports use ETL modules

---

## Test Suite 9: Regression Testing

### Test 9.1: Compare Outputs with Previous Version
**Objective**: Verify outputs match previous version (if available)

**Steps**:
1. If you have outputs from before restructuring, compare:
   - Device counts
   - Percentages
   - Site summaries
   - Burndown calculations

**Expected**:
- Numbers should match (or be explainably different if bugs were fixed)
- Formatting may differ but data should be same

**Verify**:
- [ ] Device counts match
- [ ] Calculations are consistent
- [ ] Any differences are explainable

---

## Test Suite 10: Edge Cases

### Test 10.1: Boundary Conditions
**Objective**: Test edge cases

**Steps**:
1. Test with data where:
   - All devices are ESOL 2024 (100% urgent)
   - All devices are Windows 11 upgraded (100% complete)
   - Zero devices in a category
   - Very large device counts

**Expected**:
- Scripts handle all edge cases gracefully
- No crashes or errors
- Appropriate messages displayed

**Verify**:
- [ ] Edge cases handled correctly
- [ ] No crashes
- [ ] Outputs are reasonable

---

## Test Execution Checklist

Use this checklist to track your testing progress:

### Basic Functionality
- [ ] ESOL analysis - basic run
- [ ] ESOL analysis - category filtering
- [ ] ESOL analysis - site table
- [ ] ESOL analysis - burndown
- [ ] ESOL analysis - combined options
- [ ] Win11 analysis - basic run
- [ ] Win11 analysis - site table
- [ ] Win11 analysis - burndown
- [ ] Win11 analysis - combined options
- [ ] Kiosk analysis - basic run

### Data Consistency
- [ ] Cross-script validation
- [ ] Filter logic verification

### Output Format
- [ ] Markdown report format
- [ ] CSV export format
- [ ] JSON export format

### Error Handling
- [ ] Missing data file
- [ ] Invalid arguments
- [ ] Empty data file

### Performance
- [ ] Execution time acceptable

### Integration
- [ ] Analyze.bat integration
- [ ] Dashboard integration

### Regression
- [ ] Compare with previous version (if available)

### Edge Cases
- [ ] Boundary conditions

---

## Reporting Issues

When you find issues, document:

1. **Test Case**: Which test suite and test number
2. **Steps to Reproduce**: Exact commands run
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happened
5. **Error Messages**: Full error output
6. **Environment**: Python version, OS, data file size
7. **Screenshots**: If applicable

---

## Quick Smoke Test (5 minutes)

If you only have 5 minutes, run these critical tests:

1. `python scripts/esol_count.py` - Should run without errors
2. `python scripts/win11_count.py` - Should run without errors
3. `python scripts/kiosk_count.py` - Should run without errors
4. `python scripts/esol_count.py --site-table --burndown` - Should show both features
5. Check `data/reports/` directory - Should have new report files

If all 5 pass, the basic functionality is working!

---

**Last Updated**: Based on ETL restructuring verification (November 2025)
**Estimated Total Testing Time**: 2-3 hours for full test suite

