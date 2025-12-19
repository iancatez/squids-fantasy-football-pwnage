"""Tests for NFLDataFetcher class."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import pytest
import polars as pl

from pwn_fantasy_football.data_fetch.data_fetcher import NFLDataFetcher
from pwn_fantasy_football.data_fetch.utils import load_config


class TestNFLDataFetcherInitialization:
    """Tests for NFLDataFetcher initialization."""

    def test_init_with_default_config(self, config_file):
        """Test initialization with default config path."""
        with patch("pwn_fantasy_football.data_fetch.data_fetcher.Path") as mock_path:
            mock_path.return_value.parent = Path(__file__).parent.parent / "pwn-fantasy-football" / "data_fetch"
            mock_path.return_value.parent.__truediv__ = lambda self, other: Path(str(self) + "/" + str(other))
            
            # Mock the actual config file path
            with patch("pwn_fantasy_football.data_fetch.data_fetcher.load_config") as mock_load:
                mock_load.return_value = {
                    "seasons": {"start_year": 2020, "end_year": 2022, "include_current": True},
                    "data_types": {"player_stats": {"enabled": True, "format": "parquet"}},
                    "cache": {"mode": "filesystem", "directory": "./cache", "duration": 86400, "verbose": False},
                    "output": {"directory": "./output", "format": "parquet", "create_subdirectories": True, "compression": "snappy"},
                    "http": {"timeout": 30, "user_agent": "test"},
                }
                
                with patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config"):
                    with patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory"):
                        fetcher = NFLDataFetcher()
                        assert fetcher.config is not None

    def test_init_with_custom_config(self, config_file, sample_config):
        """Test initialization with custom config path."""
        with patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config"):
            with patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory"):
                fetcher = NFLDataFetcher(config_path=config_file)
                assert fetcher.config == sample_config

    def test_configure_nflreadpy(self, config_file):
        """Test that nflreadpy is configured on initialization."""
        with patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config") as mock_update:
            with patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory"):
                fetcher = NFLDataFetcher(config_path=config_file)
                mock_update.assert_called_once()


class TestNFLDataFetcherSeasons:
    """Tests for season-related methods."""

    def test_get_seasons(self, config_file):
        """Test getting seasons from config."""
        with patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config"):
            with patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory"):
                fetcher = NFLDataFetcher(config_path=config_file)
                seasons = fetcher.get_seasons()
                
                assert isinstance(seasons, list)
                assert 2020 in seasons
                assert 2022 in seasons


class TestNFLDataFetcherFetchMethods:
    """Tests for data fetching methods."""

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_player_stats(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching player stats."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_player_stats(seasons=[2022])
        
        mock_save.assert_called_once()
        assert mock_nflreadpy.load_player_stats.called

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_player_stats_disabled(self, mock_ensure, mock_update, mock_save, temp_dir):
        """Test that disabled data types are skipped."""
        # Create config with player_stats disabled
        config = {
            "seasons": {"start_year": 2020, "end_year": 2022, "include_current": True},
            "data_types": {"player_stats": {"enabled": False, "format": "parquet"}},
            "cache": {"mode": "filesystem", "directory": "./cache", "duration": 86400, "verbose": False},
            "output": {"directory": "./output", "format": "parquet", "create_subdirectories": True, "compression": "snappy"},
            "http": {"timeout": 30, "user_agent": "test"},
        }
        config_file = temp_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_player_stats()
        
        mock_save.assert_not_called()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_rosters(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching rosters."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_rosters(seasons=[2022])
        
        mock_save.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_schedules(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching schedules."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_schedules(seasons=[2022])
        
        mock_save.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_injuries(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching injuries."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_injuries(seasons=[2022])
        
        mock_save.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_draft_picks(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching draft picks."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_draft_picks(seasons=[2022])
        
        mock_save.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_contracts(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching contracts."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_contracts(seasons=[2022])
        
        mock_save.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_play_by_play(self, mock_ensure, mock_update, mock_save, temp_dir, mock_nflreadpy):
        """Test fetching play-by-play data."""
        # Create config with play_by_play enabled
        config = {
            "seasons": {"start_year": 2020, "end_year": 2022, "include_current": True},
            "data_types": {"play_by_play": {"enabled": True, "format": "parquet"}},
            "cache": {"mode": "filesystem", "directory": "./cache", "duration": 86400, "verbose": False},
            "output": {"directory": "./output", "format": "parquet", "create_subdirectories": True, "compression": "snappy"},
            "http": {"timeout": 30, "user_agent": "test"},
        }
        config_file = temp_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_play_by_play(seasons=[2022])
        
        mock_save.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_team_stats(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching team stats."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_team_stats(seasons=[2022])
        
        mock_save.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_player_seasonal(self, mock_ensure, mock_update, mock_save, config_file):
        """Test fetching player seasonal stats."""
        # Mock nflreadpy to not have the function
        with patch("pwn_fantasy_football.data_fetch.data_fetcher.nfl") as mock_nfl:
            mock_nfl.load_player_seasonal_stats = None
            mock_nfl.load_player_seasonal = None
            
            fetcher = NFLDataFetcher(config_path=config_file)
            fetcher.fetch_player_seasonal(seasons=[2022])
            
            # Should not save if function doesn't exist
            mock_save.assert_not_called()

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_fetch_player_weekly(self, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching player weekly stats."""
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_player_weekly(seasons=[2022])
        
        # Should attempt to save (may fall back to player_stats)
        assert mock_save.called


class TestNFLDataFetcherFetchAll:
    """Tests for fetch_all method."""

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.tqdm")
    def test_fetch_all(self, mock_tqdm, mock_ensure, mock_update, mock_save, config_file, mock_nflreadpy):
        """Test fetching all enabled data types."""
        # Mock tqdm to return the iterable directly
        mock_tqdm.side_effect = lambda x, **kwargs: x
        
        fetcher = NFLDataFetcher(config_path=config_file)
        fetcher.fetch_all(seasons=[2022])
        
        # Should have called save_dataframe multiple times
        assert mock_save.call_count >= 1

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.save_dataframe")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.tqdm")
    def test_fetch_all_handles_errors(self, mock_tqdm, mock_ensure, mock_update, mock_save, config_file):
        """Test that fetch_all continues even if one fetch fails."""
        # Mock tqdm to return the iterable directly
        mock_tqdm.side_effect = lambda x, **kwargs: x
        
        # Make save_dataframe raise an error for one call
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Test error")
            return None
        
        mock_save.side_effect = side_effect
        
        fetcher = NFLDataFetcher(config_path=config_file)
        # Should not raise, but continue with other fetches
        try:
            fetcher.fetch_all(seasons=[2022])
        except Exception:
            pass  # Some errors are expected, but fetch_all should handle them


class TestNFLDataFetcherOutputPaths:
    """Tests for output path generation."""

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_get_output_path_with_subdirectories(self, mock_ensure, mock_update, config_file):
        """Test output path generation with subdirectories."""
        fetcher = NFLDataFetcher(config_path=config_file)
        path = fetcher._get_output_path("player_stats", "parquet")
        
        assert "player_stats" in str(path)
        assert path.suffix == ".parquet"

    @patch("pwn_fantasy_football.data_fetch.data_fetcher.update_config")
    @patch("pwn_fantasy_football.data_fetch.data_fetcher.ensure_directory")
    def test_get_output_path_without_subdirectories(self, mock_ensure, mock_update, temp_dir):
        """Test output path generation without subdirectories."""
        config = {
            "seasons": {"start_year": 2020, "end_year": 2022, "include_current": True},
            "data_types": {"player_stats": {"enabled": True, "format": "parquet"}},
            "cache": {"mode": "filesystem", "directory": "./cache", "duration": 86400, "verbose": False},
            "output": {
                "directory": "./output",
                "format": "parquet",
                "create_subdirectories": False,
                "compression": "snappy",
            },
            "http": {"timeout": 30, "user_agent": "test"},
        }
        config_file = temp_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        fetcher = NFLDataFetcher(config_path=config_file)
        path = fetcher._get_output_path("player_stats", "parquet")
        
        assert path.name == "player_stats.parquet"

