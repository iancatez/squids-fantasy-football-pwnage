"""
Squids Fantasy Football Pwnage - Main Package

Unified interface for data fetching and fantasy football predictions.
"""

import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import logging

from .data_fetch import NFLDataFetcher, fetch_all_data
from .prediction import FantasyPredictor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _check_data_freshness(
    data_path: Path,
    cache_duration_hours: int = 24,
    required_seasons: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Check if data exists and is fresh enough.
    
    Args:
        data_path: Path to the data file
        cache_duration_hours: Maximum age in hours before data is considered stale
        required_seasons: Optional list of seasons that must be present
        
    Returns:
        Dictionary with status information:
        {
            'exists': bool,
            'is_fresh': bool,
            'age_hours': float,
            'last_modified': datetime,
            'needs_update': bool
        }
    """
    result = {
        'exists': False,
        'is_fresh': False,
        'age_hours': None,
        'last_modified': None,
        'needs_update': True,
    }
    
    if not data_path.exists():
        logger.info(f"Data file not found: {data_path}")
        return result
    
    result['exists'] = True
    
    # Get file modification time
    mtime = os.path.getmtime(data_path)
    last_modified = datetime.fromtimestamp(mtime)
    result['last_modified'] = last_modified
    
    # Calculate age
    age = datetime.now() - last_modified
    age_hours = age.total_seconds() / 3600
    result['age_hours'] = age_hours
    
    # Check if fresh
    is_fresh = age_hours < cache_duration_hours
    result['is_fresh'] = is_fresh
    result['needs_update'] = not is_fresh
    
    if is_fresh:
        logger.info(
            f"Data file is fresh (age: {age_hours:.1f} hours, "
            f"last modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')})"
        )
    else:
        logger.info(
            f"Data file is stale (age: {age_hours:.1f} hours, "
            f"threshold: {cache_duration_hours} hours)"
        )
    
    return result


def _ensure_player_stats_data(
    data_dir: Optional[Union[str, Path]] = None,
    cache_duration_hours: int = 24,
    force_refresh: bool = False,
    seasons: Optional[List[int]] = None,
    config_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Ensure player stats data exists and is fresh.
    
    Args:
        data_dir: Directory where data is stored (default: ./data_output)
        cache_duration_hours: Maximum age before refreshing (default: 24)
        force_refresh: Force refresh even if data is fresh
        seasons: Specific seasons to fetch (None = use config)
        config_path: Path to data_fetch config file
        
    Returns:
        Path to the player stats data file
    """
    if data_dir is None:
        data_dir = Path("./data_output")
    else:
        data_dir = Path(data_dir)
    
    stats_path = data_dir / "player_stats" / "player_stats.parquet"
    
    # Check if we need to fetch/update
    status = _check_data_freshness(stats_path, cache_duration_hours)
    
    if force_refresh or status['needs_update']:
        logger.info("Fetching/updating player statistics data...")
        fetcher = NFLDataFetcher(config_path=config_path)
        
        if seasons is not None:
            fetcher.fetch_player_stats(seasons=seasons)
        else:
            fetcher.fetch_player_stats()
        
        logger.info(f"Player stats data ready at: {stats_path}")
    else:
        logger.info("Using existing player statistics data (fresh)")
    
    return stats_path


def predict_fantasy_players(
    top_n: Optional[int] = None,
    position: Optional[str] = None,
    target_season: int = 2026,
    data_dir: Optional[Union[str, Path]] = None,
    cache_duration_hours: int = 24,
    force_refresh: bool = False,
    seasons: Optional[List[int]] = None,
    data_fetch_config: Optional[Union[str, Path]] = None,
    prediction_config: Optional[Union[str, Path]] = None,
    save_predictions: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Unified CMDlet-style function to fetch data (if needed) and generate predictions.
    
    This function:
    1. Checks if player stats data exists and is fresh
    2. Fetches/updates data if needed
    3. Generates fantasy predictions with user inputs
    4. Returns results
    
    Args:
        top_n: Number of top players to return (None = all)
        position: Filter by position (QB, RB, WR, TE, or None for all)
        target_season: Season to predict for (default: 2026)
        data_dir: Directory for data storage (default: ./data_output)
        cache_duration_hours: Max age before refreshing data (default: 24)
        force_refresh: Force data refresh even if fresh (default: False)
        seasons: Specific seasons to fetch (None = use config)
        data_fetch_config: Path to data_fetch config file
        prediction_config: Path to prediction config file
        save_predictions: Whether to save predictions to file (default: True)
        **kwargs: Additional arguments passed to FantasyPredictor
        
    Returns:
        Dictionary with results:
        {
            'predictions': DataFrame with predictions,
            'top_players': DataFrame with top N players,
            'data_status': Dict with data freshness info,
            'output_path': Path to saved predictions (if saved),
            'summary': Dict with summary statistics
        }
    
    Example:
        >>> from pwn_fantasy_football import predict_fantasy_players
        >>> 
        >>> # Get top 30 QBs for 2026
        >>> results = predict_fantasy_players(
        ...     top_n=30,
        ...     position="QB",
        ...     target_season=2026
        ... )
        >>> 
        >>> # Display top players
        >>> print(results['top_players'])
        >>> 
        >>> # Get all RBs
        >>> rb_results = predict_fantasy_players(
        ...     position="RB",
        ...     force_refresh=False  # Use cached data if fresh
        ... )
    """
    start_time = time.time()
    
    # Step 1: Ensure data is available and fresh
    logger.info("=" * 80)
    logger.info("FANTASY FOOTBALL PREDICTION - Data Check & Prediction")
    logger.info("=" * 80)
    
    stats_path = _ensure_player_stats_data(
        data_dir=data_dir,
        cache_duration_hours=cache_duration_hours,
        force_refresh=force_refresh,
        seasons=seasons,
        config_path=data_fetch_config,
    )
    
    data_status = _check_data_freshness(stats_path, cache_duration_hours)
    
    # Step 2: Initialize predictor
    logger.info(f"Initializing predictor for season {target_season}...")
    
    # FantasyPredictor uses config_path and reads data_dir from config
    # We need to ensure data_dir in config matches what we're using
    predictor_kwargs = {}
    
    if prediction_config:
        predictor_kwargs['config_path'] = prediction_config
    
    predictor = FantasyPredictor(**predictor_kwargs)
    
    # Override data_dir if provided (to match what we fetched)
    if data_dir:
        predictor.data_dir = Path(data_dir)
        logger.info(f"Using data directory: {predictor.data_dir}")
    
    # Override target_season if provided
    if hasattr(predictor, 'target_season'):
        predictor.target_season = target_season
        # Also update config for consistency
        predictor.config["prediction"]["target_season"] = target_season
    
    # Step 3: Generate predictions
    logger.info("Generating predictions...")
    predictions_df = predictor.predict_all_players()
    
    # Step 4: Apply filters
    if position and position.upper() != "ALL":
        import polars as pl
        predictions_df = predictions_df.filter(pl.col("position") == position.upper())
        logger.info(f"Filtered to position: {position.upper()}")
    
    # Step 5: Get top players
    top_players = None
    if top_n:
        top_players = predictor.get_top_players(predictions_df, n=top_n)
        logger.info(f"Selected top {top_n} players")
    else:
        top_players = predictions_df
    
    # Step 6: Save predictions if requested
    output_path = None
    if save_predictions:
        output_path = predictor.save_predictions(predictions_df)
        logger.info(f"Predictions saved to: {output_path}")
    
    # Step 7: Generate summary
    elapsed_time = time.time() - start_time
    
    summary = {
        'total_players': len(predictions_df),
        'top_n': top_n if top_n else len(predictions_df),
        'position_filter': position,
        'target_season': target_season,
        'processing_time_seconds': round(elapsed_time, 2),
        'data_age_hours': data_status.get('age_hours'),
        'data_fresh': data_status.get('is_fresh'),
    }
    
    if len(predictions_df) > 0:
        import polars as pl
        summary['max_predicted_fp'] = float(predictions_df['predicted_season_fp'].max())
        summary['min_predicted_fp'] = float(predictions_df['predicted_season_fp'].min())
        summary['avg_predicted_fp'] = float(predictions_df['predicted_season_fp'].mean())
    
    logger.info("=" * 80)
    logger.info("PREDICTION COMPLETE")
    logger.info(f"Total players analyzed: {summary['total_players']}")
    logger.info(f"Processing time: {summary['processing_time_seconds']}s")
    logger.info("=" * 80)
    
    return {
        'predictions': predictions_df,
        'top_players': top_players,
        'data_status': data_status,
        'output_path': output_path,
        'summary': summary,
    }


def quick_predict(
    top_n: int = 20,
    position: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick prediction function with sensible defaults.
    
    Args:
        top_n: Number of top players (default: 20)
        position: Position filter (default: None = all positions)
        **kwargs: Additional arguments for predict_fantasy_players
        
    Returns:
        Results dictionary (see predict_fantasy_players)
    
    Example:
        >>> from pwn_fantasy_football import quick_predict
        >>> 
        >>> # Quick top 20 QBs
        >>> results = quick_predict(top_n=20, position="QB")
    """
    return predict_fantasy_players(
        top_n=top_n,
        position=position,
        **kwargs
    )


# Export main functions
__all__ = [
    "predict_fantasy_players",
    "quick_predict",
    "NFLDataFetcher",
    "FantasyPredictor",
    "fetch_all_data",
]

