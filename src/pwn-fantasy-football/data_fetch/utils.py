"""Utility functions for data processing and saving."""

import os
from pathlib import Path
from typing import Union
import polars as pl
import pandas as pd
import json


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_dataframe(
    df: Union[pl.DataFrame, pd.DataFrame],
    output_path: Union[str, Path],
    format: str = "parquet",
    compression: str = "snappy",
) -> None:
    """
    Save a DataFrame to disk in the specified format.
    
    Args:
        df: Polars or Pandas DataFrame to save
        output_path: Path where the file should be saved
        format: Output format ('parquet', 'csv', 'json')
        compression: Compression codec for parquet files
    """
    output_path = Path(output_path)
    ensure_directory(output_path.parent)
    
    # Convert pandas to polars if needed
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
    
    if format.lower() == "parquet":
        df.write_parquet(
            output_path,
            compression=compression,
        )
    elif format.lower() == "csv":
        df.write_csv(output_path)
    elif format.lower() == "json":
        df.write_json(output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_config(config_path: Union[str, Path]) -> dict:
    """Load configuration from JSON file."""
    config_path = Path(config_path)
    with open(config_path, "r") as f:
        return json.load(f)


def get_season_list(start_year: int, end_year: int, include_current: bool = True) -> list:
    """
    Generate a list of seasons from start_year to end_year.
    
    Args:
        start_year: First season to include
        end_year: Last season to include
        include_current: Whether to include the current season
        
    Returns:
        List of season years
    """
    from datetime import datetime
    
    current_year = datetime.now().year
    seasons = list(range(start_year, end_year + 1))
    
    if not include_current and current_year in seasons:
        seasons.remove(current_year)
    
    return seasons


def merge_dataframes(dfs: list[Union[pl.DataFrame, pd.DataFrame]]) -> pl.DataFrame:
    """
    Merge multiple DataFrames vertically (concatenate).
    
    Args:
        dfs: List of DataFrames to merge
        
    Returns:
        Combined DataFrame
    """
    if not dfs:
        raise ValueError("No DataFrames provided")
    
    # Convert all to polars
    polars_dfs = []
    for df in dfs:
        if isinstance(df, pd.DataFrame):
            polars_dfs.append(pl.from_pandas(df))
        else:
            polars_dfs.append(df)
    
    return pl.concat(polars_dfs)

