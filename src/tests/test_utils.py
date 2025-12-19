"""Tests for utility functions in data_fetch.utils."""

import json
import tempfile
from pathlib import Path
from datetime import datetime
import pytest
import polars as pl
import pandas as pd

from pwn_fantasy_football.data_fetch.utils import (
    ensure_directory,
    save_dataframe,
    load_config,
    get_season_list,
    merge_dataframes,
)


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_create_new_directory(self, temp_dir):
        """Test creating a new directory."""
        new_dir = temp_dir / "new_dir"
        result = ensure_directory(new_dir)
        
        assert result.exists()
        assert result.is_dir()
        assert result == new_dir

    def test_existing_directory(self, temp_dir):
        """Test with existing directory."""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()
        
        result = ensure_directory(existing_dir)
        
        assert result.exists()
        assert result.is_dir()

    def test_nested_directory_creation(self, temp_dir):
        """Test creating nested directories."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        result = ensure_directory(nested_dir)
        
        assert result.exists()
        assert result.is_dir()
        assert (temp_dir / "level1" / "level2").exists()

    def test_string_path(self, temp_dir):
        """Test with string path."""
        new_dir = temp_dir / "string_path"
        result = ensure_directory(str(new_dir))
        
        assert result.exists()
        assert isinstance(result, Path)


class TestSaveDataframe:
    """Tests for save_dataframe function."""

    def test_save_polars_parquet(self, temp_dir, sample_polars_df):
        """Test saving Polars DataFrame as Parquet."""
        output_path = temp_dir / "test.parquet"
        save_dataframe(sample_polars_df, output_path, format="parquet")
        
        assert output_path.exists()
        # Verify we can read it back
        df_read = pl.read_parquet(output_path)
        assert df_read.shape == sample_polars_df.shape
        assert df_read.columns == sample_polars_df.columns

    def test_save_pandas_parquet(self, temp_dir, sample_pandas_df):
        """Test saving Pandas DataFrame as Parquet."""
        output_path = temp_dir / "test_pandas.parquet"
        save_dataframe(sample_pandas_df, output_path, format="parquet")
        
        assert output_path.exists()
        df_read = pl.read_parquet(output_path)
        assert df_read.shape == sample_pandas_df.shape

    def test_save_csv(self, temp_dir, sample_polars_df):
        """Test saving as CSV."""
        output_path = temp_dir / "test.csv"
        save_dataframe(sample_polars_df, output_path, format="csv")
        
        assert output_path.exists()
        df_read = pl.read_csv(output_path)
        assert df_read.shape == sample_polars_df.shape

    def test_save_json(self, temp_dir, sample_polars_df):
        """Test saving as JSON."""
        output_path = temp_dir / "test.json"
        save_dataframe(sample_polars_df, output_path, format="json")
        
        assert output_path.exists()
        df_read = pl.read_json(output_path)
        assert df_read.shape == sample_polars_df.shape

    def test_creates_parent_directory(self, temp_dir, sample_polars_df):
        """Test that parent directory is created."""
        output_path = temp_dir / "nested" / "path" / "test.parquet"
        save_dataframe(sample_polars_df, output_path)
        
        assert output_path.exists()
        assert output_path.parent.exists()

    def test_invalid_format(self, temp_dir, sample_polars_df):
        """Test that invalid format raises error."""
        output_path = temp_dir / "test.invalid"
        
        with pytest.raises(ValueError, match="Unsupported format"):
            save_dataframe(sample_polars_df, output_path, format="invalid")

    def test_compression_parameter(self, temp_dir, sample_polars_df):
        """Test that compression parameter is accepted."""
        output_path = temp_dir / "test_compressed.parquet"
        save_dataframe(sample_polars_df, output_path, compression="gzip")
        
        assert output_path.exists()


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, config_file, sample_config):
        """Test loading a valid config file."""
        loaded = load_config(config_file)
        
        assert loaded == sample_config
        assert "seasons" in loaded
        assert "data_types" in loaded

    def test_load_config_string_path(self, config_file, sample_config):
        """Test loading config with string path."""
        loaded = load_config(str(config_file))
        
        assert loaded == sample_config

    def test_load_config_nonexistent_file(self, temp_dir):
        """Test loading non-existent config raises error."""
        fake_path = temp_dir / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            load_config(fake_path)


class TestGetSeasonList:
    """Tests for get_season_list function."""

    def test_basic_range(self):
        """Test basic season range."""
        seasons = get_season_list(2020, 2022)
        
        assert seasons == [2020, 2021, 2022]
        assert len(seasons) == 3

    def test_single_season(self):
        """Test single season."""
        seasons = get_season_list(2022, 2022)
        
        assert seasons == [2022]

    def test_exclude_current_year(self):
        """Test excluding current year."""
        current_year = datetime.now().year
        seasons = get_season_list(current_year - 2, current_year, include_current=False)
        
        assert current_year not in seasons
        assert current_year - 1 in seasons
        assert current_year - 2 in seasons

    def test_include_current_year(self):
        """Test including current year."""
        current_year = datetime.now().year
        seasons = get_season_list(current_year - 1, current_year, include_current=True)
        
        assert current_year in seasons

    def test_large_range(self):
        """Test large season range."""
        seasons = get_season_list(2010, 2020)
        
        assert len(seasons) == 11
        assert seasons[0] == 2010
        assert seasons[-1] == 2020


class TestMergeDataframes:
    """Tests for merge_dataframes function."""

    def test_merge_polars_dataframes(self, sample_polars_df):
        """Test merging Polars DataFrames."""
        df1 = sample_polars_df
        df2 = pl.DataFrame(
            {
                "player_id": ["999"],
                "player_name": ["Player D"],
                "season": [2022],
                "passing_yards": [500],
            }
        )
        
        result = merge_dataframes([df1, df2])
        
        assert result.shape[0] == df1.shape[0] + df2.shape[0]
        assert result.shape[1] == df1.shape[1]

    def test_merge_pandas_dataframes(self, sample_pandas_df):
        """Test merging Pandas DataFrames."""
        df1 = sample_pandas_df
        df2 = pd.DataFrame(
            {
                "player_id": ["999"],
                "player_name": ["Player D"],
                "season": [2022],
                "passing_yards": [500],
            }
        )
        
        result = merge_dataframes([df1, df2])
        
        assert isinstance(result, pl.DataFrame)
        assert result.shape[0] == df1.shape[0] + df2.shape[0]

    def test_merge_mixed_dataframes(self, sample_polars_df, sample_pandas_df):
        """Test merging mixed Polars and Pandas DataFrames."""
        result = merge_dataframes([sample_polars_df, sample_pandas_df])
        
        assert isinstance(result, pl.DataFrame)
        assert result.shape[0] == sample_polars_df.shape[0] + sample_pandas_df.shape[0]

    def test_merge_empty_list(self):
        """Test merging empty list raises error."""
        with pytest.raises(ValueError, match="No DataFrames provided"):
            merge_dataframes([])

    def test_merge_multiple_dataframes(self, sample_polars_df):
        """Test merging multiple DataFrames."""
        df1 = sample_polars_df
        df2 = sample_polars_df
        df3 = sample_polars_df
        
        result = merge_dataframes([df1, df2, df3])
        
        assert result.shape[0] == df1.shape[0] * 3

