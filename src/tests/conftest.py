"""Pytest configuration and shared fixtures."""

import json
import tempfile
from pathlib import Path
from typing import Dict
import pytest
import polars as pl
import pandas as pd


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config() -> Dict:
    """Sample configuration dictionary for testing."""
    return {
        "seasons": {
            "start_year": 2020,
            "end_year": 2022,
            "include_current": True,
        },
        "data_types": {
            "player_stats": {
                "enabled": True,
                "format": "parquet",
            },
            "rosters": {
                "enabled": True,
                "format": "parquet",
            },
            "play_by_play": {
                "enabled": False,
                "format": "parquet",
            },
        },
        "cache": {
            "mode": "filesystem",
            "directory": "./data_cache",
            "duration": 86400,
            "verbose": False,
        },
        "output": {
            "directory": "./data_output",
            "format": "parquet",
            "create_subdirectories": True,
            "compression": "snappy",
        },
        "http": {
            "timeout": 30,
            "user_agent": "test-agent",
        },
        "processing": {
            "chunk_size": 1000,
            "parallel_downloads": False,
            "max_retries": 3,
            "retry_delay": 5,
        },
    }


@pytest.fixture
def config_file(temp_dir, sample_config):
    """Create a temporary config file."""
    config_path = temp_dir / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(sample_config, f, indent=2)
    return config_path


@pytest.fixture
def sample_polars_df():
    """Create a sample Polars DataFrame for testing."""
    return pl.DataFrame(
        {
            "player_id": ["123", "456", "789"],
            "player_name": ["Player A", "Player B", "Player C"],
            "season": [2022, 2022, 2022],
            "passing_yards": [300, 250, 400],
        }
    )


@pytest.fixture
def sample_pandas_df():
    """Create a sample Pandas DataFrame for testing."""
    return pd.DataFrame(
        {
            "player_id": ["123", "456", "789"],
            "player_name": ["Player A", "Player B", "Player C"],
            "season": [2022, 2022, 2022],
            "passing_yards": [300, 250, 400],
        }
    )


@pytest.fixture
def mock_nflreadpy(monkeypatch):
    """Mock nflreadpy functions for testing."""
    mock_data = pl.DataFrame(
        {
            "player_id": ["123", "456"],
            "player_name": ["Test Player 1", "Test Player 2"],
            "season": [2022, 2022],
        }
    )

    def mock_load_player_stats(seasons):
        return mock_data

    def mock_load_rosters(seasons):
        return mock_data

    def mock_load_schedules(seasons):
        return mock_data

    def mock_load_injuries(seasons):
        return mock_data

    def mock_load_draft_picks(seasons):
        return mock_data

    def mock_load_contracts(seasons):
        return mock_data

    def mock_load_pbp(seasons):
        return mock_data

    def mock_load_team_stats(seasons):
        return mock_data

    # Create a mock nfl module
    class MockNFL:
        load_player_stats = staticmethod(mock_load_player_stats)
        load_rosters = staticmethod(mock_load_rosters)
        load_schedules = staticmethod(mock_load_schedules)
        load_injuries = staticmethod(mock_load_injuries)
        load_draft_picks = staticmethod(mock_load_draft_picks)
        load_contracts = staticmethod(mock_load_contracts)
        load_pbp = staticmethod(mock_load_pbp)
        load_team_stats = staticmethod(mock_load_team_stats)

    monkeypatch.setattr("pwn_fantasy_football.data_fetch.data_fetcher.nfl", MockNFL())
    return MockNFL

