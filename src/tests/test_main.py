"""Tests for the CLI main module."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import the main module
from pwn_fantasy_football.data_fetch.main import main as main_function


class TestMainCLI:
    """Tests for command-line interface."""

    @patch("pwn_fantasy_football.data_fetch.main.NFLDataFetcher")
    def test_main_fetch_all(self, mock_fetcher_class):
        """Test main function with --data-type all."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock sys.argv
        test_args = ["main.py", "--data-type", "all"]
        with patch.object(sys, "argv", test_args):
            main_function()
        
        mock_fetcher.fetch_all.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.main.NFLDataFetcher")
    def test_main_fetch_specific_type(self, mock_fetcher_class):
        """Test main function with specific data type."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        test_args = ["main.py", "--data-type", "player_stats"]
        with patch.object(sys, "argv", test_args):
            main_function()
        
        mock_fetcher.fetch_player_stats.assert_called_once()

    @patch("pwn_fantasy_football.data_fetch.main.NFLDataFetcher")
    def test_main_with_seasons(self, mock_fetcher_class):
        """Test main function with specific seasons."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        test_args = ["main.py", "--data-type", "player_stats", "--seasons", "2022", "2023"]
        with patch.object(sys, "argv", test_args):
            main_function()
        
        mock_fetcher.fetch_player_stats.assert_called_once_with(seasons=[2022, 2023])

    @patch("pwn_fantasy_football.data_fetch.main.NFLDataFetcher")
    def test_main_with_config(self, mock_fetcher_class):
        """Test main function with custom config."""
        mock_fetcher = MagicMock()
        mock_fetcher_class.return_value = mock_fetcher
        
        test_args = ["main.py", "--config", "custom_config.json", "--data-type", "all"]
        with patch.object(sys, "argv", test_args):
            main_function()
        
        mock_fetcher_class.assert_called_once()
        # Check that config_path was passed
        call_args = mock_fetcher_class.call_args
        assert call_args[1]["config_path"] == Path("custom_config.json")

