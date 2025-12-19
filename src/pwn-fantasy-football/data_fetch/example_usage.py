"""Example usage of the NFL data fetcher."""

from pathlib import Path
from .data_fetcher import NFLDataFetcher, fetch_all_data


def example_basic_usage():
    """Basic example: fetch all data using default config."""
    print("Fetching all data with default configuration...")
    fetch_all_data()


def example_custom_config():
    """Example: use a custom configuration file."""
    custom_config = Path(__file__).parent / "cfg" / "cfg.json"
    fetcher = NFLDataFetcher(custom_config)
    fetcher.fetch_all()


def example_selective_fetch():
    """Example: fetch only specific data types."""
    fetcher = NFLDataFetcher()
    
    # Fetch only player stats and rosters
    fetcher.fetch_player_stats()
    fetcher.fetch_rosters()


def example_specific_seasons():
    """Example: fetch data for specific seasons only."""
    fetcher = NFLDataFetcher()
    
    # Fetch only 2022 and 2023 seasons
    seasons = [2022, 2023]
    fetcher.fetch_player_stats(seasons=seasons)
    fetcher.fetch_rosters(seasons=seasons)


if __name__ == "__main__":
    # Run the basic example
    example_basic_usage()
    
    # Uncomment to try other examples:
    # example_custom_config()
    # example_selective_fetch()
    # example_specific_seasons()

