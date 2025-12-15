#!/usr/bin/env python3
"""Test script to verify penalty thresholds from config affect scores."""
import sys
from pathlib import Path
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from etl.analysis.okr_aggregator import OKRAggregator

def test_penalty_thresholds():
    """Test that changing penalty thresholds affects scores."""
    print("=" * 80)
    print("TESTING PENALTY THRESHOLDS")
    print("=" * 80)
    
    # Test data: 0.5% ESOL 2024, 2% ESOL 2025
    esol_counts = {
        'esol_2024': 5,  # 0.5% of 1000 devices
        'esol_2025': 20,  # 2% of 1000 devices
        'total_devices': 1000
    }
    win11_counts = {
        'win11_adoption_pct': 90.0,
        'total_enterprise': 1000
    }
    kiosk_counts = {
        'enterprise_count': 0
    }
    
    # Test 1: Default thresholds (1.0% for KR1, 5.0% for KR2)
    print("\nTest 1: Default thresholds (KR1: 1.0%, KR2: 5.0%)")
    mock_config1 = Mock()
    mock_config1.get_okr_criteria.return_value = {
        'okr_weights': {
            'kr1_esol_2024': 25,
            'kr2_esol_2025': 25,
            'kr3_win11_compatibility': 40,
            'kr4_kiosk_reprovisioning': 10
        },
        'targets': {
            'kr1_target_percentage': 0,
            'kr2_target_percentage': 0,
            'kr3_target_percentage': 90,
            'kr4_target_count': 0
        },
        'status_thresholds': {
            'caution_min_progress': 60,
            'on_track_min_progress': 80
        },
        'penalty_thresholds': {
            'kr1_penalty_threshold_percentage': 1.0,
            'kr2_penalty_threshold_percentage': 5.0
        }
    }
    mock_config1.get_esol_criteria.return_value = {
        'esol_categories': {}
    }
    
    aggregator1 = OKRAggregator(mock_config1)
    scores1 = aggregator1.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)
    
    print(f"  KR1: 0.5% ESOL 2024 → Score: {scores1['kr1_score']:.1f}")
    print(f"  KR2: 2.0% ESOL 2025 → Score: {scores1['kr2_score']:.1f}")
    
    # Test 2: Lower thresholds (0.5% for KR1, 2.0% for KR2) - should give lower scores
    print("\nTest 2: Lower thresholds (KR1: 0.5%, KR2: 2.0%)")
    mock_config2 = Mock()
    mock_config2.get_okr_criteria.return_value = {
        'okr_weights': {
            'kr1_esol_2024': 25,
            'kr2_esol_2025': 25,
            'kr3_win11_compatibility': 40,
            'kr4_kiosk_reprovisioning': 10
        },
        'targets': {
            'kr1_target_percentage': 0,
            'kr2_target_percentage': 0,
            'kr3_target_percentage': 90,
            'kr4_target_count': 0
        },
        'status_thresholds': {
            'caution_min_progress': 60,
            'on_track_min_progress': 80
        },
        'penalty_thresholds': {
            'kr1_penalty_threshold_percentage': 0.5,  # Lower threshold
            'kr2_penalty_threshold_percentage': 2.0   # Lower threshold
        }
    }
    mock_config2.get_esol_criteria.return_value = {
        'esol_categories': {}
    }
    
    aggregator2 = OKRAggregator(mock_config2)
    scores2 = aggregator2.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)
    
    print(f"  KR1: 0.5% ESOL 2024 → Score: {scores2['kr1_score']:.1f}")
    print(f"  KR2: 2.0% ESOL 2025 → Score: {scores2['kr2_score']:.1f}")
    
    # Test 3: Higher thresholds (2.0% for KR1, 10.0% for KR2) - should give higher scores
    print("\nTest 3: Higher thresholds (KR1: 2.0%, KR2: 10.0%)")
    mock_config3 = Mock()
    mock_config3.get_okr_criteria.return_value = {
        'okr_weights': {
            'kr1_esol_2024': 25,
            'kr2_esol_2025': 25,
            'kr3_win11_compatibility': 40,
            'kr4_kiosk_reprovisioning': 10
        },
        'targets': {
            'kr1_target_percentage': 0,
            'kr2_target_percentage': 0,
            'kr3_target_percentage': 90,
            'kr4_target_count': 0
        },
        'status_thresholds': {
            'caution_min_progress': 60,
            'on_track_min_progress': 80
        },
        'penalty_thresholds': {
            'kr1_penalty_threshold_percentage': 2.0,  # Higher threshold
            'kr2_penalty_threshold_percentage': 10.0  # Higher threshold
        }
    }
    mock_config3.get_esol_criteria.return_value = {
        'esol_categories': {}
    }
    
    aggregator3 = OKRAggregator(mock_config3)
    scores3 = aggregator3.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)
    
    print(f"  KR1: 0.5% ESOL 2024 → Score: {scores3['kr1_score']:.1f}")
    print(f"  KR2: 2.0% ESOL 2025 → Score: {scores3['kr2_score']:.1f}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION:")
    print("=" * 80)
    print(f"✓ Scores change with different thresholds:")
    print(f"  KR1 scores: {scores1['kr1_score']:.1f} (1.0%) → {scores2['kr1_score']:.1f} (0.5%) → {scores3['kr1_score']:.1f} (2.0%)")
    print(f"  KR2 scores: {scores1['kr2_score']:.1f} (5.0%) → {scores2['kr2_score']:.1f} (2.0%) → {scores3['kr2_score']:.1f} (10.0%)")
    
    # Verify scores are different
    assert scores1['kr1_score'] != scores2['kr1_score'], "KR1 scores should differ with different thresholds"
    assert scores1['kr2_score'] != scores2['kr2_score'], "KR2 scores should differ with different thresholds"
    assert scores1['kr1_score'] != scores3['kr1_score'], "KR1 scores should differ with different thresholds"
    assert scores1['kr2_score'] != scores3['kr2_score'], "KR2 scores should differ with different thresholds"
    
    print("✓ All assertions passed - config changes now affect scores!")
    print("=" * 80)

if __name__ == "__main__":
    test_penalty_thresholds()
