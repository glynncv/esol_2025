#!/usr/bin/env python3
"""Shared data utilities for EUC analysis scripts."""

import os
import argparse
from pathlib import Path

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
        if Path(user_path).exists():
            return user_path
        else:
            raise FileNotFoundError(f"Specified data file not found: {user_path}")
    
    # Check environment variable
    env_path = os.getenv('EUC_DATA_FILE')
    if env_path and Path(env_path).exists():
        return env_path
    
    # Default path
    default_path = 'data/raw/EUC_ESOL.xlsx'
    if Path(default_path).exists():
        return default_path
    
    # Try CSV fallback
    csv_fallback = 'data/raw/EUC_ESOL.csv'
    if Path(csv_fallback).exists():
        return csv_fallback
    
    raise FileNotFoundError(
        f"No data file found. Checked paths:\n"
        f"  - User provided: {user_path}\n"
        f"  - Environment (EUC_DATA_FILE): {env_path}\n"
        f"  - Default Excel: {default_path}\n"
        f"  - Fallback CSV: {csv_fallback}\n"
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
