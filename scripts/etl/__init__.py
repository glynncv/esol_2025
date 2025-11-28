"""ETL (Extract, Transform, Load) package for EUC device analysis.

This package provides centralized data processing capabilities following the ETL pattern:
1. DATA CAPTURE - load_data.py
2. CLEAN & TRANSFORM - transform.py (future)
3. ANALYSIS - analysis/ modules (future)
4. NORMALIZE - normalize.py (future)
5. PRESENTATION - presentation/ modules (future)
"""

from .load_data import DataLoader

__all__ = ['DataLoader']
