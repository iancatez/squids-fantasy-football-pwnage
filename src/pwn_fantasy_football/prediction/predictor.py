"""Fantasy football player prediction algorithm."""

from pathlib import Path
from typing import Dict, List, Optional
import logging
import json

import polars as pl

from .fantasy_calculator import FantasyPointCalculator

logger = logging.getLogger(__name__)


class FantasyPredictor:
    """Predict fantasy football performance for upcoming season."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the fantasy predictor.
        
        Args:
            config_path: Path to configuration JSON file. If None, uses default path.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "cfg" / "cfg.json"
        
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        self.data_dir = Path(self.config["data"]["data_output_dir"])
        self.calculator = FantasyPointCalculator(self.config.get("scoring", {}))
        self.target_season = self.config["prediction"]["target_season"]
        
    def load_player_stats(self) -> pl.DataFrame:
        """Load historical player statistics."""
        stats_path = self.data_dir / "player_stats" / "player_stats.parquet"
        
        if not stats_path.exists():
            raise FileNotFoundError(
                f"Player stats not found at {stats_path}. "
                "Please run data_fetch first to download data."
            )
        
        logger.info(f"Loading player stats from {stats_path}")
        df = pl.read_parquet(stats_path)
        
        # Convert position to string immediately if it exists
        if "position" in df.columns:
            # Handle position column - convert lists to strings using map_elements
            df = df.with_columns([
                pl.col("position").map_elements(
                    lambda x: (
                        x[0] if isinstance(x, list) and len(x) > 0 
                        else (str(x) if x is not None else "UNK")
                    ),
                    return_dtype=pl.Utf8
                ).alias("position")
            ])
        
        # Calculate fantasy points
        df = self.calculator.calculate_fantasy_points(df)
        
        return df
    
    def get_player_seasonal_stats(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Aggregate player stats by season.
        
        Args:
            df: Game-level player statistics
            
        Returns:
            DataFrame with seasonal aggregates
        """
        # Position should already be string from load_player_stats, but ensure it
        # (in case this method is called with a different dataframe)
        if "position" in df.columns:
            df = df.with_columns(
                pl.col("position").cast(pl.Utf8).alias("position")
            )
        
        # Group by player and season
        seasonal = df.group_by(["player_id", "player_name", "season", "position"]).agg([
            pl.sum("fantasy_points").alias("total_fp"),
            pl.mean("fantasy_points").alias("avg_fp_per_game"),
            pl.count().alias("games_played"),
            pl.std("fantasy_points").alias("fp_std"),
            pl.min("fantasy_points").alias("min_fp"),
            pl.max("fantasy_points").alias("max_fp"),
        ])
        
        # Ensure position remains string type after grouping
        if "position" in seasonal.columns:
            seasonal = seasonal.with_columns(
                pl.col("position").cast(pl.Utf8).alias("position")
            )
        
        # Calculate consistency (lower std = more consistent)
        # Handle None/NaN values in fp_std
        seasonal = seasonal.with_columns(
            pl.when(pl.col("fp_std").is_null() | pl.col("fp_std").is_nan())
            .then(pl.lit(0.5))  # Default consistency for missing std
            .otherwise(1.0 / (pl.col("fp_std") + 1.0))
            .alias("consistency_score")
        )
        
        return seasonal
    
    def calculate_trend(self, seasonal_df: pl.DataFrame, player_id: str) -> float:
        """
        Calculate performance trend for a player (improving/declining).
        
        Args:
            seasonal_df: Seasonal statistics DataFrame
            player_id: Player ID to analyze
            
        Returns:
            Trend score (positive = improving, negative = declining)
        """
        player_data = seasonal_df.filter(pl.col("player_id") == player_id)
        
        if len(player_data) < 2:
            return 0.0
        
        # Sort by season
        player_data = player_data.sort("season")
        
        # Calculate linear trend in average FP per game
        seasons = player_data["season"].to_list()
        avg_fp = player_data["avg_fp_per_game"].to_list()
        
        # Filter out None values
        valid_data = [(s, f) for s, f in zip(seasons, avg_fp) if f is not None and not (isinstance(f, float) and (f != f))]  # f != f checks for NaN
        
        if len(valid_data) < 2:
            return 0.0
        
        seasons, avg_fp = zip(*valid_data)
        seasons = list(seasons)
        avg_fp = list(avg_fp)
        
        # Simple linear regression slope
        n = len(seasons)
        sum_x = sum(seasons)
        sum_y = sum(avg_fp)
        sum_xy = sum(s * f for s, f in zip(seasons, avg_fp))
        sum_x2 = sum(s * s for s in seasons)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        return slope
    
    def predict_player_2026(self, seasonal_df: pl.DataFrame, player_id: str) -> Dict:
        """
        Predict a player's 2026 fantasy performance.
        
        Args:
            seasonal_df: Seasonal statistics DataFrame
            player_id: Player ID to predict
            
        Returns:
            Dictionary with prediction details
        """
        player_data = seasonal_df.filter(pl.col("player_id") == player_id)
        
        if len(player_data) == 0:
            return None
        
        # Get player info - handle position extraction carefully
        player_row = player_data.to_dicts()[0]  # Convert to dict to handle types properly
        player_name = player_row.get("player_name", "Unknown")
        position_raw = player_row.get("position")
        
        # Handle position - convert from any format to string
        if isinstance(position_raw, list):
            position = position_raw[0] if position_raw else "UNK"
        elif position_raw is None:
            position = "UNK"
        else:
            position = str(position_raw)
        
        # Filter to recent seasons (last 3 years)
        recent_data = player_data.filter(
            pl.col("season") >= self.target_season - 3
        )
        
        if len(recent_data) == 0:
            return None
        
        # Base prediction: weighted average of recent seasons
        recent_seasons = recent_data["season"].to_list()
        recent_avg_fp = recent_data["avg_fp_per_game"].to_list()
        
        # Filter out None/NaN values
        valid_data = [(s, f) for s, f in zip(recent_seasons, recent_avg_fp) 
                     if f is not None and not (isinstance(f, float) and (f != f))]
        
        if not valid_data:
            return None
        
        recent_seasons, recent_avg_fp = zip(*valid_data)
        recent_seasons = list(recent_seasons)
        recent_avg_fp = list(recent_avg_fp)
        
        # Weight more recent seasons higher
        weights = [1.0 + (i * 0.3) for i in range(len(recent_avg_fp))]
        weights.reverse()  # Most recent gets highest weight
        
        weighted_avg = sum(f * w for f, w in zip(recent_avg_fp, weights)) / sum(weights)
        
        # Calculate trend
        trend = self.calculate_trend(seasonal_df, player_id)
        trend_adjustment = trend * self.config["prediction"].get("trend_weight", 0.3)
        
        # Calculate consistency (handle None values)
        consistency_scores = recent_data["consistency_score"].to_list()
        consistency_scores = [c for c in consistency_scores if c is not None and not (isinstance(c, float) and (c != c))]
        if consistency_scores:
            consistency = sum(consistency_scores) / len(consistency_scores)
        else:
            consistency = 0.5  # Default
        consistency_bonus = (consistency - 0.5) * self.config["prediction"].get("consistency_weight", 0.2)
        
        # Final prediction
        predicted_fp = weighted_avg + trend_adjustment + consistency_bonus
        
        # Ensure non-negative
        predicted_fp = max(0.0, predicted_fp)
        
        # Project to full season (17 games)
        predicted_season_fp = predicted_fp * 17
        
        # Ensure position is a string (not list)
        if isinstance(position, list):
            position_str = position[0] if position else "UNK"
        elif position is None:
            position_str = "UNK"
        else:
            position_str = str(position)
        
        return {
            "player_id": player_id,
            "player_name": player_name,
            "position": position_str,
            "predicted_avg_fp_per_game": round(predicted_fp, 2),
            "predicted_season_fp": round(predicted_season_fp, 2),
            "recent_avg_fp": round(recent_data["avg_fp_per_game"].mean(), 2),
            "trend": round(trend, 3),
            "consistency_score": round(consistency, 3),
            "seasons_analyzed": len(recent_data),
            "last_season": recent_data["season"].max(),
        }
    
    def predict_all_players(self) -> pl.DataFrame:
        """
        Predict fantasy performance for all eligible players.
        
        Returns:
            DataFrame with predictions sorted by predicted season FP
        """
        logger.info("Loading and processing player statistics...")
        df = self.load_player_stats()
        
        logger.info("Calculating seasonal statistics...")
        seasonal_df = self.get_player_seasonal_stats(df)
        
        # Filter to players with minimum seasons played
        min_seasons = self.config["prediction"].get("min_seasons_played", 2)
        player_season_counts = seasonal_df.group_by("player_id").agg([
            pl.count().alias("season_count")
        ])
        
        eligible_players = player_season_counts.filter(
            pl.col("season_count") >= min_seasons
        )["player_id"].to_list()
        
        # Filter by position if specified
        position_filters = self.config["prediction"].get("position_filters", {})
        if any(position_filters.values()):
            allowed_positions = [
                pos for pos, enabled in position_filters.items() if enabled
            ]
            eligible_players = seasonal_df.filter(
                (pl.col("player_id").is_in(eligible_players))
                & (pl.col("position").is_in(allowed_positions))
            )["player_id"].unique().to_list()
        
        logger.info(f"Predicting for {len(eligible_players)} eligible players...")
        
        predictions = []
        for player_id in eligible_players:
            try:
                prediction = self.predict_player_2026(seasonal_df, player_id)
                if prediction:
                    predictions.append(prediction)
            except Exception as e:
                logger.warning(f"Error predicting for player {player_id}: {e}")
                continue
        
        if not predictions:
            raise ValueError("No predictions generated. Check data and filters.")
        
        predictions_df = pl.DataFrame(predictions)
        
        # Position should already be string from predict_player_2026, but ensure it
        # Convert any remaining lists or ensure it's Utf8 type
        if "position" in predictions_df.columns:
            # First try to cast directly, if that fails, use map_elements
            try:
                predictions_df = predictions_df.with_columns(
                    pl.col("position").cast(pl.Utf8).alias("position")
                )
            except Exception:
                # If cast fails (e.g., because of lists), use map_elements
                predictions_df = predictions_df.with_columns([
                    pl.col("position").map_elements(
                        lambda pos: (
                            pos[0] if isinstance(pos, list) and pos 
                            else (str(pos) if pos is not None else "UNK")
                        ),
                        return_dtype=pl.Utf8
                    ).alias("position")
                ])
        
        predictions_df = predictions_df.sort("predicted_season_fp", descending=True)
        
        return predictions_df
    
    def save_predictions(self, predictions_df: pl.DataFrame) -> Path:
        """
        Save predictions to file.
        
        Args:
            predictions_df: DataFrame with predictions
            
        Returns:
            Path to saved file
        """
        output_dir = Path(self.config["output"]["directory"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_format = self.config["output"].get("format", "parquet")
        output_path = output_dir / f"predictions_2026.{output_format}"
        
        if output_format == "parquet":
            predictions_df.write_parquet(output_path)
        elif output_format == "csv":
            predictions_df.write_csv(output_path)
        else:
            predictions_df.write_json(output_path)
        
        logger.info(f"Saved predictions to {output_path}")
        return output_path
    
    def get_top_players(self, predictions_df: pl.DataFrame, n: Optional[int] = None) -> pl.DataFrame:
        """
        Get top N predicted players.
        
        Args:
            predictions_df: DataFrame with predictions
            n: Number of top players to return. If None, uses config value.
            
        Returns:
            DataFrame with top N players
        """
        if n is None:
            n = self.config["output"].get("top_n_players", 50)
        
        return predictions_df.head(n)

