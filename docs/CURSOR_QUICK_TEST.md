# Quick Cursor Testing Prompt (Copy & Paste)

Copy and paste this into Cursor to start testing:

---

## Testing Task: ETL Restructuring Verification

I need you to verify the ETL restructuring on branch `claude/etl-pipeline-review-011CUtcvdKFSfLMorNPnf6wu`.

**Steps**:

1. **Setup**: Create a worktree and switch to the branch
   ```bash
   git fetch origin
   git worktree add ../esol_2025_testing claude/etl-pipeline-review-011CUtcvdKFSfLMorNPnf6wu
   cd ../esol_2025_testing
   ```

2. **Review Architecture**: Read `docs/ETL_ARCHITECTURE.md` and summarize the 3 main layers

3. **Verify Structure**: Check all ETL modules exist:
   - `scripts/etl/load_data.py`
   - `scripts/etl/analysis/*.py` (4 files)
   - `scripts/etl/presentation/*.py` (5 files)
   - `scripts/tests/test_*.py` (3 files)

4. **Compile Test**: Verify all files compile
   ```bash
   cd scripts
   python3 -m py_compile esol_count.py win11_count.py kiosk_count.py
   python3 -m py_compile etl/analysis/*.py etl/presentation/*.py
   ```

5. **Run Unit Tests**:
   ```bash
   cd scripts/tests
   python3 run_tests.py -v
   ```
   Report: How many tests run? How many pass?

6. **Verify Separation**: Check that analyzers have NO format methods
   ```bash
   cd scripts
   grep -n "def format_" etl/analysis/*.py  # Should be EMPTY
   grep -n "def format_" etl/presentation/*.py  # Should have results
   ```

7. **Test Imports**:
   ```bash
   python3 -c "from etl.load_data import DataLoader; from etl.analysis import ESOLAnalyzer, Win11Analyzer; from etl.presentation import ESOLFormatter; print('All imports OK')"
   ```

8. **Code Metrics**: Count lines and calculate reduction percentage
   ```bash
   wc -l esol_count.py win11_count.py kiosk_count.py
   wc -l etl/analysis/*.py etl/presentation/*.py
   wc -l tests/test_*.py
   ```

**Report back**:
- ✓/✗ for each step
- Any errors or issues found
- Confirmation that architecture is clean
- Test results summary
- Code metrics comparison

See `docs/CURSOR_TESTING_PROMPT.md` for detailed instructions.
