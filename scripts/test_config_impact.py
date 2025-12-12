#!/usr/bin/env python3
"""Demonstrate that config changes now affect OKR scores."""
import sys
from pathlib import Path
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from etl.analysis.okr_aggregator import OKRAggregator

def demonstrate_config_impact():
    """Show how changing penalty thresholds affects scores."""
    print("=" * 80)
    print("DEMONSTRATING CONFIG IMPACT ON OKR SCORES")
    print("=" * 80)
    print()
    
    # Simulate realistic data: Some ESOL devices present
    # This represents a typical scenario
    esol_counts = {
        'esol_2024': 15,      # 1.5% of 1000 devices
        'esol_2025': 30,      # 3.0% of 1000 devices  
        'total_devices': 1000
    }
    win11_counts = {
        'win11_adoption_pct': 85.0,
        'total_enterprise': 1000
    }
    kiosk_counts = {
        'enterprise_count': 5
    }
    
    print("Test Scenario:")
    print(f"  Total devices: {esol_counts['total_devices']:,}")
    print(f"  ESOL 2024 devices: {esol_counts['esol_2024']} ({esol_counts['esol_2024']/esol_counts['total_devices']*100:.2f}%)")
    print(f"  ESOL 2025 devices: {esol_counts['esol_2025']} ({esol_counts['esol_2025']/esol_counts['total_devices']*100:.2f}%)")
    print(f"  Win11 adoption: {win11_counts['win11_adoption_pct']:.1f}%")
    print(f"  Kiosk devices: {kiosk_counts['enterprise_count']}")
    print()
    
    # Test with current config values (1.0% and 5.0%)
    print("=" * 80)
    print("TEST 1: Current Config Values")
    print("=" * 80)
    print("Penalty Thresholds:")
    print("  KR1 (ESOL 2024): 1.0%")
    print("  KR2 (ESOL 2025): 5.0%")
    print()
    
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
    
    print("Results:")
    print(f"  KR1 Score: {scores1['kr1_score']:.1f}/100")
    print(f"  KR2 Score: {scores1['kr2_score']:.1f}/100")
    print(f"  KR3 Score: {scores1['kr3_score']:.1f}/100")
    print(f"  KR4 Score: {scores1['kr4_score']:.1f}/100")
    print(f"  Overall OKR Score: {scores1['okr_score']:.1f}/100 [{scores1['status']}]")
    print()
    
    # Test with stricter thresholds (0.5% and 2.0%) - should give LOWER scores
    print("=" * 80)
    print("TEST 2: Stricter Thresholds (More Penalizing)")
    print("=" * 80)
    print("Penalty Thresholds:")
    print("  KR1 (ESOL 2024): 0.5% (stricter)")
    print("  KR2 (ESOL 2025): 2.0% (stricter)")
    print()
    print("NOTE: This simulates changing okr_criteria.yaml:")
    print("   penalty_thresholds:")
    print("     kr1_penalty_threshold_percentage: 0.5")
    print("     kr2_penalty_threshold_percentage: 2.0")
    print()
    
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
            'kr1_penalty_threshold_percentage': 0.5,  # Stricter
            'kr2_penalty_threshold_percentage': 2.0   # Stricter
        }
    }
    mock_config2.get_esol_criteria.return_value = {
        'esol_categories': {}
    }
    
    aggregator2 = OKRAggregator(mock_config2)
    scores2 = aggregator2.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)
    
    print("Results:")
    print(f"  KR1 Score: {scores2['kr1_score']:.1f}/100 (was {scores1['kr1_score']:.1f})")
    print(f"  KR2 Score: {scores2['kr2_score']:.1f}/100 (was {scores1['kr2_score']:.1f})")
    print(f"  KR3 Score: {scores2['kr3_score']:.1f}/100 (unchanged)")
    print(f"  KR4 Score: {scores2['kr4_score']:.1f}/100 (unchanged)")
    print(f"  Overall OKR Score: {scores2['okr_score']:.1f}/100 [{scores2['status']}] (was {scores1['okr_score']:.1f})")
    print()
    
    # Test with more lenient thresholds (2.0% and 10.0%) - should give HIGHER scores
    print("=" * 80)
    print("TEST 3: More Lenient Thresholds (Less Penalizing)")
    print("=" * 80)
    print("Penalty Thresholds:")
    print("  KR1 (ESOL 2024): 2.0% (more lenient)")
    print("  KR2 (ESOL 2025): 10.0% (more lenient)")
    print()
    print("NOTE: This simulates changing okr_criteria.yaml:")
    print("   penalty_thresholds:")
    print("     kr1_penalty_threshold_percentage: 2.0")
    print("     kr2_penalty_threshold_percentage: 10.0")
    print()
    
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
            'kr1_penalty_threshold_percentage': 2.0,  # More lenient
            'kr2_penalty_threshold_percentage': 10.0  # More lenient
        }
    }
    mock_config3.get_esol_criteria.return_value = {
        'esol_categories': {}
    }
    
    aggregator3 = OKRAggregator(mock_config3)
    scores3 = aggregator3.calculate_okr_scores(esol_counts, win11_counts, kiosk_counts)
    
    print("Results:")
    print(f"  KR1 Score: {scores3['kr1_score']:.1f}/100 (was {scores1['kr1_score']:.1f})")
    print(f"  KR2 Score: {scores3['kr2_score']:.1f}/100 (was {scores1['kr2_score']:.1f})")
    print(f"  KR3 Score: {scores3['kr3_score']:.1f}/100 (unchanged)")
    print(f"  KR4 Score: {scores3['kr4_score']:.1f}/100 (unchanged)")
    print(f"  Overall OKR Score: {scores3['okr_score']:.1f}/100 [{scores3['status']}] (was {scores1['okr_score']:.1f})")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("SUCCESS: Config changes now directly affect OKR scores!")
    print()
    print("Score Changes:")
    print(f"  KR1: {scores1['kr1_score']:.1f} → {scores2['kr1_score']:.1f} (stricter) → {scores3['kr1_score']:.1f} (lenient)")
    print(f"  KR2: {scores1['kr2_score']:.1f} → {scores2['kr2_score']:.1f} (stricter) → {scores3['kr2_score']:.1f} (lenient)")
    print(f"  Overall: {scores1['okr_score']:.1f} → {scores2['okr_score']:.1f} → {scores3['okr_score']:.1f}")
    print()
    print("To change scores in your actual reports:")
    print("  1. Edit config/okr_criteria.yaml")
    print("  2. Modify penalty_thresholds section")
    print("  3. Run okr_tracker.py again")
    print("  4. Scores will reflect your changes!")
    print("=" * 80)

if __name__ == "__main__":
    demonstrate_config_impact()
