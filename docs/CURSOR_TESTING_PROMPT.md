# Cursor Testing Prompt: ETL Restructuring Verification

## Context

The ESOL 2025 project has completed a comprehensive 5-phase ETL restructuring (November 2025). All changes are on branch `claude/etl-pipeline-review-011CUtcvdKFSfLMorNPnf6wu`.

**Your task**: Pull this branch, create a clean worktree for testing, and verify the restructured codebase works correctly.

## Phase 1: Setup Worktree

Create a new worktree for testing the ETL restructuring:

```bash
# Navigate to repository
cd /path/to/esol_2025

# Fetch latest changes
git fetch origin

# Create a new worktree for testing
git worktree add ../esol_2025_etl_testing claude/etl-pipeline-review-011CUtcvdKFSfLMorNPnf6wu

# Navigate to the testing worktree
cd ../esol_2025_etl_testing

# Verify branch
git branch --show-current
# Should output: claude/etl-pipeline-review-011CUtcvdKFSfLMorNPnf6wu

# Check status
git status
# Should be clean
```

## Phase 2: Review Documentation

Before testing, review the comprehensive documentation:

1. **Read** `docs/ETL_ARCHITECTURE.md` - Understand the complete architecture
2. **Read** `docs/DEVELOPER_GUIDE.md` - Learn the development patterns
3. **Review** `README.md` - See the updated project structure

**Questions to answer**:
- What are the 3 main ETL layers?
- Which commit corresponds to each phase (1-5)?
- What was the total impact in lines of code?

## Phase 3: Verify File Structure

Check that all ETL modules are present:

```bash
# Check ETL structure
ls -la scripts/etl/
ls -la scripts/etl/analysis/
ls -la scripts/etl/presentation/
ls -la scripts/tests/

# Expected structure:
# scripts/etl/
#   __init__.py
#   load_data.py
#   analysis/
#     __init__.py
#     esol_analyzer.py
#     win11_analyzer.py
#     kiosk_analyzer.py
#     burndown_calculator.py
#   presentation/
#     __init__.py
#     esol_formatter.py
#     win11_formatter.py
#     kiosk_formatter.py
#     burndown_formatter.py
#     file_exporter.py
# scripts/tests/
#   __init__.py
#   test_win11_analyzer.py
#   test_formatters.py
#   test_burndown_calculator.py
#   run_tests.py
#   README.md
```

**Task**: Verify all files exist and report any missing files.

## Phase 4: Code Compilation Testing

Verify all Python files compile without syntax errors:

```bash
cd scripts

# Test main analysis scripts
python3 -m py_compile esol_count.py
python3 -m py_compile win11_count.py
python3 -m py_compile kiosk_count.py

# Test ETL modules
python3 -m py_compile etl/load_data.py
python3 -m py_compile etl/analysis/*.py
python3 -m py_compile etl/presentation/*.py

# Test unit tests
python3 -m py_compile tests/test_*.py
```

**Expected**: All files should compile without errors.

**Task**: Report any compilation errors. If errors exist, investigate and suggest fixes.

## Phase 5: Run Unit Tests

Execute the comprehensive unit test suite:

```bash
cd scripts/tests

# Run all tests with verbose output
python3 run_tests.py -v

# Expected output should show:
# - test_win11_analyzer: 4 tests
# - test_formatters: 10 tests
# - test_burndown_calculator: 6 tests
# - Total: ~20 tests, all passing
```

**Task**:
1. Run the tests
2. Report the results (pass/fail count)
3. If any tests fail, investigate why and suggest fixes
4. Verify test coverage matches expectations

## Phase 6: Architecture Verification

Verify the separation of concerns is maintained:

```bash
cd scripts

# Check that analyzers contain NO formatting methods
grep -n "def format_" etl/analysis/*.py
# Should return NOTHING (formatters were removed in Phase 4)

# Check that formatters contain formatting methods
grep -n "def format_" etl/presentation/*.py
# Should find multiple format_ methods

# Verify ConfigManager usage (no hardcoded columns)
grep -n "'Action to take'" esol_count.py win11_count.py kiosk_count.py
# Should return NOTHING (should use config_manager)
```

**Task**:
- Verify analyzers have NO format methods
- Verify formatters HAVE format methods
- Check for any hardcoded column names in scripts
- Report any violations of separation of concerns

## Phase 7: Import Testing

Verify all ETL imports work correctly:

```bash
cd scripts

# Test imports work
python3 -c "from etl.load_data import DataLoader; print('✓ DataLoader imports')"
python3 -c "from etl.analysis import ESOLAnalyzer, Win11Analyzer, KioskAnalyzer, BurndownCalculator; print('✓ Analyzers import')"
python3 -c "from etl.presentation import ESOLFormatter, Win11Formatter, KioskFormatter, BurndownFormatter, FileExporter; print('✓ Formatters import')"
```

**Expected**: All imports should succeed.

**Task**: Report import status. If imports fail, check for missing __init__.py files or circular dependencies.

## Phase 8: Code Quality Review

Review the code quality improvements:

```bash
cd scripts

# Count lines in main scripts (should be smaller than before)
wc -l esol_count.py win11_count.py kiosk_count.py

# Count lines in ETL modules
wc -l etl/load_data.py
wc -l etl/analysis/*.py
wc -l etl/presentation/*.py

# Count lines in tests
wc -l tests/test_*.py
```

**Task**:
1. Calculate total lines for:
   - Main scripts (esol_count, win11_count, kiosk_count)
   - ETL modules (load_data + analysis + presentation)
   - Unit tests
2. Compare to documentation claims:
   - Scripts should be 42-60% smaller than before
   - Total duplication eliminated: 944 lines
   - Tests added: 187 lines

## Phase 9: Documentation Completeness

Verify documentation is comprehensive:

```bash
# Check documentation exists
ls -la docs/ETL_ARCHITECTURE.md
ls -la docs/DEVELOPER_GUIDE.md
ls -la scripts/tests/README.md

# Check documentation size
wc -l docs/ETL_ARCHITECTURE.md     # Should be ~500 lines
wc -l docs/DEVELOPER_GUIDE.md      # Should be ~350 lines
wc -l scripts/tests/README.md      # Should be ~70 lines
```

**Task**:
1. Verify all documentation files exist
2. Check documentation is comprehensive (not stubs)
3. Verify code examples in docs are accurate
4. Report any outdated or incorrect documentation

## Phase 10: Integration Testing (Optional - Requires Data)

If you have access to test data, verify end-to-end functionality:

```bash
cd scripts

# Test ESOL analysis (requires data/raw/EUC_ESOL.xlsx)
python3 esol_count.py --category all

# Test Win11 analysis
python3 win11_count.py

# Test Kiosk analysis
python3 kiosk_count.py

# Check outputs are generated
ls -la data/reports/
```

**Note**: This step requires actual data file. Skip if data not available.

**Task** (if data available):
1. Run each analysis script
2. Verify reports are generated in data/reports/
3. Verify console output is formatted correctly
4. Check for any runtime errors

## Phase 11: Git History Review

Review the commit history to understand the restructuring:

```bash
# View commit history for this branch
git log --oneline --graph origin/main..HEAD

# Should see 5 commits for 5 phases:
# - dace081: Phase 5: Documentation and cleanup
# - 9efa375: Phase 4: Complete separation of concerns and add tests
# - d32fbfc: Phase 3: Extract presentation formatters
# - 274ec22: Phase 2: Extract business logic to reusable modules
# - bc18f97: Phase 1: Centralize data loading

# View detailed changes for each phase
git show bc18f97 --stat  # Phase 1
git show 274ec22 --stat  # Phase 2
git show d32fbfc --stat  # Phase 3
git show 9efa375 --stat  # Phase 4
git show dace081 --stat  # Phase 5
```

**Task**:
1. Verify all 5 phase commits are present
2. Review commit messages for completeness
3. Check file change statistics match documentation claims

## Success Criteria

Mark each as ✓ or ✗:

- [ ] All files present in correct structure
- [ ] All Python files compile without errors
- [ ] All unit tests pass (20+ tests)
- [ ] Analyzers contain NO format methods
- [ ] Formatters contain format methods
- [ ] No hardcoded column names in scripts
- [ ] All ETL imports work correctly
- [ ] Scripts are 42-60% smaller than before
- [ ] Documentation is comprehensive and accurate
- [ ] All 5 phase commits are present
- [ ] Git history is clean and well-documented

## Final Report

After completing all phases, provide a summary report:

**Architecture Verification**: ✓/✗
- DataLoader separation:
- Analyzer separation:
- Formatter separation:

**Testing Status**: X/20 tests passing
- Win11Analyzer tests:
- Formatter tests:
- BurndownCalculator tests:

**Code Quality**:
- Total lines in scripts:
- Total lines in ETL modules:
- Total lines in tests:
- Scripts size reduction: X%

**Issues Found**: (list any issues)

**Recommendations**: (suggest any improvements)

## Cleanup

When testing is complete:

```bash
# Return to main repository
cd /path/to/esol_2025

# Remove testing worktree (optional)
git worktree remove ../esol_2025_etl_testing
```

---

**Note to Cursor**: Follow this prompt step-by-step. Report your findings for each phase. If you encounter issues, investigate and suggest fixes before proceeding.
