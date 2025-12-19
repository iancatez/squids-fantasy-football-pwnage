"""Main data fetching module for NFL data using nflreadpy."""

import os
from pathlib import Path
from typing import Optional, Union, List
import logging
import time
from tqdm import tqdm

import nflreadpy as nfl
from nflreadpy.config import update_config

from .utils import (
    ensure_directory,
    save_dataframe,
    load_config,
    get_season_list,
    merge_dataframes,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class NFLDataFetcher:
    """Main class for fetching NFL data using nflreadpy."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize the data fetcher with configuration.
        
        Args:
            config_path: Path to configuration JSON file. If None, uses default path.
        """
        if config_path is None:
            # Default to cfg.json in the cfg directory
            config_path = Path(__file__).parent / "cfg" / "cfg.json"
        
        self.config = load_config(config_path)
        self._configure_nflreadpy()
        self.output_dir = Path(self.config["output"]["directory"])
        ensure_directory(self.output_dir)
        
    def _configure_nflreadpy(self) -> None:
        """Configure nflreadpy based on config settings."""
        cache_config = self.config.get("cache", {})
        http_config = self.config.get("http", {})
        
        # Convert cache_dir to Path object if it's a string
        cache_dir = cache_config.get("directory", "./data_cache")
        if isinstance(cache_dir, str):
            cache_dir = Path(cache_dir)
        
        update_config(
            cache_mode=cache_config.get("mode", "filesystem"),
            cache_dir=cache_dir,
            cache_duration=cache_config.get("duration", 86400),
            verbose=cache_config.get("verbose", True),
            timeout=http_config.get("timeout", 30),
            user_agent=http_config.get("user_agent", "pwn-fantasy-football/0.1.0"),
        )
        logger.info("nflreadpy configuration updated")
    
    def get_seasons(self) -> List[int]:
        """Get list of seasons to fetch based on config."""
        seasons_config = self.config.get("seasons", {})
        return get_season_list(
            start_year=seasons_config.get("start_year", 2010),
            end_year=seasons_config.get("end_year", 2024),
            include_current=seasons_config.get("include_current", True),
        )
    
    def fetch_player_stats(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch player game-level statistics.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("player_stats", {})
        if not data_config.get("enabled", True):
            logger.info("player_stats is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching player stats for seasons: {seasons}")
        
        try:
            # Fetch data
            if hasattr(nfl, "load_player_stats"):
                df = nfl.load_player_stats(seasons)
            else:
                logger.error("load_player_stats not available in nflreadpy")
                raise AttributeError("load_player_stats not found in nflreadpy")
            
            # Save data
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("player_stats", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved player stats to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}", exc_info=True)
            raise
    
    def fetch_player_seasonal(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch player seasonal statistics.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("player_seasonal", {})
        if not data_config.get("enabled", True):
            logger.info("player_seasonal is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching player seasonal stats for seasons: {seasons}")
        
        try:
            # Try different possible function names for seasonal stats
            if hasattr(nfl, "load_player_seasonal_stats"):
                df = nfl.load_player_seasonal_stats(seasons)
            elif hasattr(nfl, "load_player_seasonal"):
                df = nfl.load_player_seasonal(seasons)
            else:
                logger.warning("Player seasonal stats function not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("player_seasonal", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved player seasonal stats to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching player seasonal stats: {e}", exc_info=True)
            raise
    
    def fetch_player_weekly(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch player weekly statistics.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("player_weekly", {})
        if not data_config.get("enabled", True):
            logger.info("player_weekly is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching player weekly stats for seasons: {seasons}")
        
        try:
            # Try different possible function names for weekly stats
            if hasattr(nfl, "load_player_weekly_stats"):
                df = nfl.load_player_weekly_stats(seasons)
            elif hasattr(nfl, "load_player_weekly"):
                df = nfl.load_player_weekly(seasons)
            else:
                # Player stats might already be weekly, so we can use that
                logger.info("Player weekly stats function not found, using player_stats instead...")
                if hasattr(nfl, "load_player_stats"):
                    df = nfl.load_player_stats(seasons)
                else:
                    logger.warning("load_player_stats not available in nflreadpy, skipping...")
                    return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("player_weekly", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved player weekly stats to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching player weekly stats: {e}", exc_info=True)
            raise
    
    def fetch_team_stats(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch team statistics.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("team_stats", {})
        if not data_config.get("enabled", True):
            logger.info("team_stats is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching team stats for seasons: {seasons}")
        
        try:
            if hasattr(nfl, "load_team_stats"):
                df = nfl.load_team_stats(seasons)
            elif hasattr(nfl, "load_team_seasonal_stats"):
                df = nfl.load_team_seasonal_stats(seasons)
            else:
                logger.warning("Team stats function not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("team_stats", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved team stats to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching team stats: {e}", exc_info=True)
            raise
    
    def fetch_rosters(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch roster data.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("rosters", {})
        if not data_config.get("enabled", True):
            logger.info("rosters is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching rosters for seasons: {seasons}")
        
        try:
            if hasattr(nfl, "load_rosters"):
                df = nfl.load_rosters(seasons)
            else:
                logger.warning("load_rosters not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("rosters", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved rosters to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching rosters: {e}", exc_info=True)
            raise
    
    def fetch_schedules(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch schedule data.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("schedules", {})
        if not data_config.get("enabled", True):
            logger.info("schedules is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching schedules for seasons: {seasons}")
        
        try:
            if hasattr(nfl, "load_schedules"):
                df = nfl.load_schedules(seasons)
            else:
                logger.warning("load_schedules not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("schedules", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved schedules to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching schedules: {e}", exc_info=True)
            raise
    
    def fetch_injuries(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch injury data.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("injuries", {})
        if not data_config.get("enabled", True):
            logger.info("injuries is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching injuries for seasons: {seasons}")
        
        try:
            if hasattr(nfl, "load_injuries"):
                df = nfl.load_injuries(seasons)
            else:
                logger.warning("load_injuries not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("injuries", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved injuries to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching injuries: {e}", exc_info=True)
            raise
    
    def fetch_draft_picks(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch draft pick data.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("draft_picks", {})
        if not data_config.get("enabled", True):
            logger.info("draft_picks is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching draft picks for seasons: {seasons}")
        
        try:
            if hasattr(nfl, "load_draft_picks"):
                df = nfl.load_draft_picks(seasons)
            else:
                logger.warning("load_draft_picks not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("draft_picks", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved draft picks to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching draft picks: {e}", exc_info=True)
            raise
    
    def fetch_contracts(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch contract data.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("contracts", {})
        if not data_config.get("enabled", True):
            logger.info("contracts is disabled in config, skipping...")
            return
        
        logger.info("Fetching contracts...")
        
        try:
            if hasattr(nfl, "load_contracts"):
                # load_contracts() doesn't take seasons parameter
                df = nfl.load_contracts()
            else:
                logger.warning("load_contracts not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("contracts", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved contracts to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching contracts: {e}", exc_info=True)
            raise
    
    def fetch_play_by_play(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch play-by-play data (large dataset).
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        if seasons is None:
            seasons = self.get_seasons()
        
        data_config = self.config["data_types"].get("play_by_play", {})
        if not data_config.get("enabled", False):
            logger.info("play_by_play is disabled in config, skipping...")
            return
        
        logger.info(f"Fetching play-by-play data for seasons: {seasons}")
        logger.warning("Play-by-play data is large and may take significant time to download")
        
        try:
            # nflreadpy uses load_pbp for play-by-play data
            if hasattr(nfl, "load_pbp"):
                df = nfl.load_pbp(seasons)
            else:
                logger.warning("load_pbp not available in nflreadpy, skipping...")
                return
            
            output_format = data_config.get("format", "parquet")
            output_path = self._get_output_path("play_by_play", output_format)
            compression = self.config["output"].get("compression", "snappy")
            
            save_dataframe(df, output_path, format=output_format, compression=compression)
            logger.info(f"Saved play-by-play data to {output_path}")
            
        except Exception as e:
            logger.error(f"Error fetching play-by-play data: {e}", exc_info=True)
            raise
    
    def fetch_all(self, seasons: Optional[List[int]] = None) -> None:
        """
        Fetch all enabled data types.
        
        Args:
            seasons: List of seasons to fetch. If None, uses config seasons.
        """
        logger.info("Starting comprehensive data fetch...")
        start_time = time.time()
        
        fetch_methods = [
            ("Player Stats", self.fetch_player_stats),
            ("Player Seasonal", self.fetch_player_seasonal),
            ("Player Weekly", self.fetch_player_weekly),
            ("Team Stats", self.fetch_team_stats),
            ("Rosters", self.fetch_rosters),
            ("Schedules", self.fetch_schedules),
            ("Injuries", self.fetch_injuries),
            ("Draft Picks", self.fetch_draft_picks),
            ("Contracts", self.fetch_contracts),
            ("Play-by-Play", self.fetch_play_by_play),
        ]
        
        for name, method in tqdm(fetch_methods, desc="Fetching data"):
            try:
                method(seasons)
            except Exception as e:
                logger.error(f"Failed to fetch {name}: {e}")
                # Continue with other data types even if one fails
        
        elapsed_time = time.time() - start_time
        logger.info(f"Data fetch completed in {elapsed_time:.2f} seconds")
    
    def _get_output_path(self, data_type: str, format: str) -> Path:
        """
        Generate output path for a data type.
        
        Args:
            data_type: Type of data (e.g., 'player_stats')
            format: File format (e.g., 'parquet')
            
        Returns:
            Path object for the output file
        """
        if self.config["output"].get("create_subdirectories", True):
            output_path = self.output_dir / data_type / f"{data_type}.{format}"
        else:
            output_path = self.output_dir / f"{data_type}.{format}"
        
        return output_path


def fetch_all_data(config_path: Optional[Union[str, Path]] = None) -> None:
    """
    Convenience function to fetch all data using default configuration.
    
    Args:
        config_path: Path to configuration file. If None, uses default.
    """
    fetcher = NFLDataFetcher(config_path)
    fetcher.fetch_all()

