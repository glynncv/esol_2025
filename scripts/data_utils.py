#!/usr/bin/env python3
"""Shared data utilities for EUC analysis scripts."""

import os
import argparse
from pathlib import Path

def _find_project_root():
    """Find project root by looking for common markers (data/, config/, etc.)."""
    current = Path(__file__).resolve().parent
    # Go up from scripts/ to project root
    while current.parent != current:
        if (current / 'data').exists() and (current / 'config').exists():
            return current
        current = current.parent
    # Fallback: assume we're in scripts/, so go up one level
    return Path(__file__).resolve().parent.parent

def get_data_file_path(user_path=None):
    """Get data file path with fallback logic.
    
    Args:
        user_path: Explicitly provided file path
        
    Returns:
        str: Path to the data file
        
    Raises:
        FileNotFoundError: If no valid data file is found
    """
    # Check explicitly provided path first
    if user_path:
        user_path_obj = Path(user_path)
        if user_path_obj.exists():
            return str(user_path_obj.resolve())
        else:
            raise FileNotFoundError(f"Specified data file not found: {user_path}")
    
    # Check environment variable
    env_path = os.getenv('EUC_DATA_FILE')
    if env_path:
        env_path_obj = Path(env_path)
        if env_path_obj.exists():
            return str(env_path_obj.resolve())
    
    # Try multiple locations for default paths
    project_root = _find_project_root()
    possible_paths = [
        project_root / 'data' / 'raw' / 'EUC_ESOL.xlsx',  # Project root
        Path('data/raw/EUC_ESOL.xlsx'),  # Current directory
        Path('../data/raw/EUC_ESOL.xlsx'),  # From scripts/ directory
        project_root / 'data' / 'raw' / 'EUC_ESOL.csv',  # CSV fallback from project root
        Path('data/raw/EUC_ESOL.csv'),  # CSV fallback from current directory
        Path('../data/raw/EUC_ESOL.csv'),  # CSV fallback from scripts/
    ]
    
    checked_paths = []
    for path in possible_paths:
        checked_paths.append(str(path.resolve()) if path.is_absolute() or path.exists() else str(path))
        if path.exists():
            return str(path.resolve())
    
    raise FileNotFoundError(
        f"No data file found. Checked paths:\n"
        f"  - User provided: {user_path}\n"
        f"  - Environment (EUC_DATA_FILE): {env_path}\n"
        f"  - Possible locations:\n" + "\n".join(f"    - {p}" for p in checked_paths) + "\n"
        f"Set EUC_DATA_FILE environment variable or ensure default file exists."
    )

def add_data_file_argument(parser, default_description="Path to EUC_ESOL.xlsx file"):
    """Add standardized data file argument to argument parser.
    
    Args:
        parser: argparse.ArgumentParser instance
        default_description: Description for the help text
        
    Returns:
        argparse.ArgumentParser: The parser with data file argument added
    """
    parser.add_argument(
        'data_file', 
        nargs='?', 
        default=None,
        help=f'{default_description} (default: auto-detect from data/raw/ or EUC_DATA_FILE env var)'
    )
    return parser

def validate_data_file(data_file_path):
    """Validate that the data file exists and is readable.
    
    Args:
        data_file_path: Path to the data file
        
    Returns:
        bool: True if file is valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file is not readable
    """
    path = Path(data_file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {data_file_path}")
    
    if not path.is_file():
        raise FileNotFoundError(f"Path is not a file: {data_file_path}")
    
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Data file is not readable: {data_file_path}")
    
    return True
