# ETL Module Unit Tests

This directory contains unit tests for the ETL (Extract, Transform, Load) modules.

## Test Coverage

- **test_win11_analyzer.py**: Tests for Win11Analyzer class
  - KPI metrics calculation (calculate_kpi_metrics)
  - Edge cases (zero eligible, 100% complete, etc.)

- **test_formatters.py**: Tests for presentation formatters
  - Win11Formatter (markdown reports, console output, KPI sections)
  - ESOLFormatter (all categories, single category reports)
  - KioskFormatter (markdown reports)
  - BurndownFormatter (ESOL and Win11 burndown reports)

- **test_burndown_calculator.py**: Tests for BurndownCalculator class
  - ESOL burndown calculations (multiple categories)
  - Win11 burndown calculations
  - Edge cases (zero devices, past deadline, complete)

## Running Tests

### Run all tests:
```bash
cd scripts/tests
python3 run_tests.py
```

### Run specific test file:
```bash
cd scripts/tests
python3 -m unittest test_win11_analyzer.py
```

### Run specific test class:
```bash
cd scripts/tests
python3 -m unittest test_win11_analyzer.TestWin11Analyzer
```

### Run specific test method:
```bash
cd scripts/tests
python3 -m unittest test_win11_analyzer.TestWin11Analyzer.test_calculate_kpi_metrics_basic
```

## Test Requirements

Tests use Python's built-in `unittest` framework and `unittest.mock` for mocking dependencies.

No additional test dependencies are required beyond the main project requirements (pandas, PyYAML).

## Adding New Tests

1. Create a new test file following the naming convention `test_<module_name>.py`
2. Import unittest and the module to test
3. Create test classes inheriting from `unittest.TestCase`
4. Add test methods prefixed with `test_`
5. Use `setUp()` for common test fixtures
6. Run tests to verify they pass

## Test Philosophy

- **Unit tests**: Test individual methods in isolation
- **Mock external dependencies**: Use mocks for ConfigManager, file I/O
- **Test edge cases**: Zero values, negative values, boundary conditions
- **Clear assertions**: Each test should verify specific behavior
- **Descriptive names**: Test names should describe what they test
