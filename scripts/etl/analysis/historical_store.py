"""Historical data storage for OKR tracking and trend analysis.

This module provides the HistoricalDataStore class which persists OKR snapshots
over time to enable trend analysis and week-over-week comparisons.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd


class HistoricalDataStore:
    """Store and retrieve historical OKR snapshots for trend analysis.

    Snapshots are stored as JSON files in data/history/ directory with
    timestamp-based filenames for chronological ordering.
    """

    def __init__(self, history_dir: str = 'data/history'):
        """Initialize historical data store.

        Args:
            history_dir: Directory to store historical snapshots
        """
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, overall_scores: Dict, country_scores: pd.DataFrame,
                     sdm_scores: pd.DataFrame, site_scores: pd.DataFrame,
                     timestamp: Optional[datetime] = None) -> Path:
        """Save OKR snapshot to historical storage.

        Args:
            overall_scores: Dict from OKRAggregator.calculate_okr_scores()
            country_scores: DataFrame from OKRAggregator.aggregate_by_country()
            sdm_scores: DataFrame from OKRAggregator.aggregate_by_sdm()
            site_scores: DataFrame from OKRAggregator.aggregate_by_site()
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Path to saved snapshot file
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Create snapshot data structure
        snapshot = {
            'timestamp': timestamp.isoformat(),
            'overall_scores': overall_scores,
            'country_scores': country_scores.to_dict('records') if len(country_scores) > 0 else [],
            'sdm_scores': sdm_scores.to_dict('records') if len(sdm_scores) > 0 else [],
            'site_scores': site_scores.to_dict('records') if len(site_scores) > 0 else []
        }

        # Generate filename with timestamp
        filename = f"okr_snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.history_dir / filename

        # Save to JSON
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)

        return filepath

    def get_latest_snapshot(self) -> Optional[Dict]:
        """Get the most recent snapshot.

        Returns:
            Snapshot dict or None if no snapshots exist
        """
        snapshots = self._list_snapshot_files()
        if not snapshots:
            return None

        latest_file = snapshots[-1]  # Files are sorted chronologically
        return self._load_snapshot(latest_file)

    def get_previous_snapshot(self, days_back: int = 7) -> Optional[Dict]:
        """Get snapshot from approximately N days ago.

        Args:
            days_back: Number of days to look back (default: 7 for week-over-week)

        Returns:
            Snapshot dict or None if not found
        """
        target_date = datetime.now() - timedelta(days=days_back)
        snapshots = self._list_snapshot_files()

        if not snapshots:
            return None

        # Find closest snapshot to target date
        best_match = None
        min_diff = None

        for snapshot_file in snapshots:
            snapshot = self._load_snapshot(snapshot_file)
            snapshot_time = datetime.fromisoformat(snapshot['timestamp'])
            diff = abs((snapshot_time - target_date).total_seconds())

            if min_diff is None or diff < min_diff:
                min_diff = diff
                best_match = snapshot

        return best_match

    def get_snapshots_in_range(self, start_date: datetime,
                               end_date: Optional[datetime] = None) -> List[Dict]:
        """Get all snapshots within a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range (defaults to now)

        Returns:
            List of snapshot dicts sorted chronologically
        """
        if end_date is None:
            end_date = datetime.now()

        snapshots = []
        for snapshot_file in self._list_snapshot_files():
            snapshot = self._load_snapshot(snapshot_file)
            snapshot_time = datetime.fromisoformat(snapshot['timestamp'])

            if start_date <= snapshot_time <= end_date:
                snapshots.append(snapshot)

        return snapshots

    def get_all_snapshots(self) -> List[Dict]:
        """Get all historical snapshots.

        Returns:
            List of all snapshot dicts sorted chronologically
        """
        return [self._load_snapshot(f) for f in self._list_snapshot_files()]

    def count_snapshots(self) -> int:
        """Get total number of snapshots stored.

        Returns:
            Count of snapshots
        """
        return len(self._list_snapshot_files())

    def _list_snapshot_files(self) -> List[Path]:
        """List all snapshot files sorted chronologically.

        Returns:
            List of snapshot file paths
        """
        snapshot_files = list(self.history_dir.glob('okr_snapshot_*.json'))
        return sorted(snapshot_files)  # Timestamp in filename ensures chronological order

    def _load_snapshot(self, filepath: Path) -> Dict:
        """Load snapshot from JSON file.

        Args:
            filepath: Path to snapshot file

        Returns:
            Snapshot dict
        """
        with open(filepath, 'r') as f:
            snapshot = json.load(f)

        # Convert list records back to DataFrames for easier manipulation
        snapshot['country_scores_df'] = pd.DataFrame(snapshot['country_scores'])
        snapshot['sdm_scores_df'] = pd.DataFrame(snapshot['sdm_scores'])
        snapshot['site_scores_df'] = pd.DataFrame(snapshot['site_scores'])

        return snapshot
