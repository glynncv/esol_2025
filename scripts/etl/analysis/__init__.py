"""Analysis module for EUC device business logic and KPI calculations."""
from .burndown_calculator import BurndownCalculator
from .esol_analyzer import ESOLAnalyzer
from .win11_analyzer import Win11Analyzer
from .kiosk_analyzer import KioskAnalyzer
from .okr_aggregator import OKRAggregator

__all__ = [
    'BurndownCalculator',
    'ESOLAnalyzer',
    'Win11Analyzer',
    'KioskAnalyzer',
    'OKRAggregator'
]
