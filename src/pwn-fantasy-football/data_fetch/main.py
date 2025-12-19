"""Main entry point for data fetching."""

import argparse
from pathlib import Path
from .data_fetcher import NFLDataFetcher, fetch_all_data


def main():
    """Main function to run data fetching."""
    parser = argparse.ArgumentParser(
        description="Fetch NFL data using nflreadpy for ML training"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration JSON file (default: cfg/cfg.json)",
    )
    parser.add_argument(
        "--data-type",
        type=str,
        choices=[
            "all",
            "player_stats",
            "player_seasonal",
            "player_weekly",
            "team_stats",
            "rosters",
            "schedules",
            "injuries",
            "draft_picks",
            "contracts",
            "play_by_play",
        ],
        default="all",
        help="Type of data to fetch (default: all)",
    )
    parser.add_argument(
        "--seasons",
        type=int,
        nargs="+",
        default=None,
        help="Specific seasons to fetch (e.g., --seasons 2022 2023). If not provided, uses config.",
    )
    
    args = parser.parse_args()
    
    # Initialize fetcher
    config_path = args.config
    if config_path:
        config_path = Path(config_path)
    
    fetcher = NFLDataFetcher(config_path)
    
    # Fetch data based on arguments
    if args.data_type == "all":
        if args.seasons:
            fetcher.fetch_all(seasons=args.seasons)
        else:
            fetcher.fetch_all()
    else:
        seasons = args.seasons if args.seasons else None
        method_name = f"fetch_{args.data_type}"
        method = getattr(fetcher, method_name)
        method(seasons=seasons)


if __name__ == "__main__":
    main()

