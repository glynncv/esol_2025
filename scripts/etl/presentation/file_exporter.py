"""File export utilities for saving analysis results."""
from pathlib import Path
from datetime import datetime
from typing import Tuple, Union, Dict, List, Optional
import json
import pandas as pd


class FileExporter:
    """Centralized file export utilities for analysis results.

    Handles file I/O operations including auto-save logic and directory creation.
    """

    @staticmethod
    def save_report(content: str, output_path: Union[str, Path] = None,
                   auto_prefix: str = 'Report', auto_suffix: str = '') -> Path:
        """Save report content to file with auto-save support.

        Args:
            content: Report content to save
            output_path: Optional user-specified output path
            auto_prefix: Prefix for auto-generated filename
            auto_suffix: Suffix for auto-generated filename (before timestamp)

        Returns:
            Path where file was saved
        """
        if output_path:
            # User specified output path
            file_path = Path(output_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Auto-save to data/reports/ with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path('data/reports')
            output_dir.mkdir(parents=True, exist_ok=True)

            if auto_suffix:
                filename = f'{auto_prefix}_{auto_suffix}_{timestamp}.md'
            else:
                filename = f'{auto_prefix}_{timestamp}.md'

            file_path = output_dir / filename

        # Write content
        file_path.write_text(content, encoding='utf-8')
        return file_path

    @staticmethod
    def export_json_csv(data: Union[list, dict], filename_prefix: str,
                       output_dir: Union[str, Path] = 'data/processed') -> Tuple[Path, Path]:
        """Export data to both JSON and CSV files.

        Args:
            data: Data to export (list of dicts or single dict)
            filename_prefix: Prefix for output filenames
            output_dir: Directory for output files (default: data/processed)

        Returns:
            Tuple of (json_path, csv_path)
        """
        import pandas as pd

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export as JSON
        json_file = output_path / f'{filename_prefix}_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Export as CSV
        csv_file = output_path / f'{filename_prefix}_{timestamp}.csv'
        if isinstance(data, list):
            # List of dicts
            df = pd.DataFrame(data)
        else:
            # Single dict
            df = pd.DataFrame([data])
        df.to_csv(csv_file, index=False)

        return (json_file, csv_file)

    @staticmethod
    def export_okr_to_excel(overall_scores: Dict,
                           country_scores: pd.DataFrame,
                           sdm_scores: pd.DataFrame,
                           site_scores: pd.DataFrame,
                           historical_snapshots: Optional[List[Dict]] = None,
                           output_path: Union[str, Path] = None) -> Path:
        """Export OKR dashboard data to Excel with multiple sheets.

        Args:
            overall_scores: Dict from OKRAggregator.calculate_okr_scores()
            country_scores: DataFrame from OKRAggregator.aggregate_by_country()
            sdm_scores: DataFrame from OKRAggregator.aggregate_by_sdm()
            site_scores: DataFrame from OKRAggregator.aggregate_by_site()
            historical_snapshots: Optional list of historical snapshots
            output_path: Optional user-specified output path

        Returns:
            Path where Excel file was saved
        """
        if output_path:
            file_path = Path(output_path)
            if not file_path.suffix:
                file_path = file_path.with_suffix('.xlsx')
            file_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Auto-save to data/processed/ with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path('data/processed')
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = output_dir / f'OKR_Dashboard_{timestamp}.xlsx'

        # Create Excel writer
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Sheet 1: Overall Summary
            overall_df = pd.DataFrame([{
                'Metric': 'OKR Score',
                'Value': f"{overall_scores['okr_score']:.1f}",
                'Status': overall_scores['status'],
                'Total Devices': overall_scores['total_devices']
            }])

            kr_df = pd.DataFrame([
                {
                    'Key Result': 'KR1 - ESOL 2024 Remediation',
                    'Score': f"{overall_scores['kr1_score']:.1f}",
                    'Value': overall_scores['kr1_value'],
                    'Percentage': f"{overall_scores['kr1_pct']:.2f}%"
                },
                {
                    'Key Result': 'KR2 - ESOL 2025 Remediation',
                    'Score': f"{overall_scores['kr2_score']:.1f}",
                    'Value': overall_scores['kr2_value'],
                    'Percentage': f"{overall_scores['kr2_pct']:.2f}%"
                },
                {
                    'Key Result': 'KR3 - Windows 11 Adoption',
                    'Score': f"{overall_scores['kr3_score']:.1f}",
                    'Value': f"{overall_scores['kr3_value']:.1f}%",
                    'Percentage': 'N/A'
                },
                {
                    'Key Result': 'KR4 - Kiosk Re-provisioning',
                    'Score': f"{overall_scores['kr4_score']:.1f}",
                    'Value': overall_scores['kr4_value'],
                    'Percentage': 'N/A'
                }
            ])

            overall_df.to_excel(writer, sheet_name='Overall Summary', index=False)
            kr_df.to_excel(writer, sheet_name='Key Results', index=False, startrow=5)

            # Sheet 2: Country Breakdown
            if len(country_scores) > 0:
                country_scores.to_excel(writer, sheet_name='Country Breakdown', index=False)

            # Sheet 3: SDM Performance
            if len(sdm_scores) > 0:
                sdm_scores.to_excel(writer, sheet_name='SDM Performance', index=False)

            # Sheet 4: Site Details
            if len(site_scores) > 0:
                site_scores.to_excel(writer, sheet_name='Site Details', index=False)

            # Sheet 5: Historical Trends (if available)
            if historical_snapshots and len(historical_snapshots) > 1:
                history_df = pd.DataFrame([
                    {
                        'Timestamp': snapshot['timestamp'],
                        'OKR Score': snapshot['overall_scores']['okr_score'],
                        'KR1 Score': snapshot['overall_scores']['kr1_score'],
                        'KR2 Score': snapshot['overall_scores']['kr2_score'],
                        'KR3 Score': snapshot['overall_scores']['kr3_score'],
                        'KR4 Score': snapshot['overall_scores']['kr4_score'],
                        'Total Devices': snapshot['overall_scores']['total_devices']
                    }
                    for snapshot in historical_snapshots
                ])
                history_df.to_excel(writer, sheet_name='Historical Trends', index=False)

        return file_path
