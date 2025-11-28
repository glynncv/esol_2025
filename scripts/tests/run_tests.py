#!/usr/bin/env python3
"""Test runner for ETL module unit tests."""
import unittest
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run ETL module unit tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output (same as verbosity=2)')
    parser.add_argument('--verbosity', type=int, choices=[0, 1, 2], default=2,
                       help='Verbosity level: 0=quiet, 1=normal, 2=verbose (default: 2)')
    args = parser.parse_args()
    
    # Determine verbosity level
    verbosity = 2 if args.verbose else args.verbosity
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
