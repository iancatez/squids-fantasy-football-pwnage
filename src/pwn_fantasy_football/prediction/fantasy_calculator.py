"""Fantasy football point calculator."""

from typing import Dict, Optional
import polars as pl


class FantasyPointCalculator:
    """Calculate fantasy football points from player statistics."""
    
    def __init__(self, scoring_config: Optional[Dict] = None):
        """
        Initialize the fantasy point calculator.
        
        Args:
            scoring_config: Dictionary with scoring rules. If None, uses standard scoring.
        """
        if scoring_config is None:
            scoring_config = {
                "passing_yards": 0.04,
                "passing_tds": 4,
                "interceptions": -2,
                "rushing_yards": 0.1,
                "rushing_tds": 6,
                "receptions": 0.5,
                "receiving_yards": 0.1,
                "receiving_tds": 6,
                "fumbles_lost": -2,
                "two_point_conversions": 2,
            }
        
        self.scoring = scoring_config
    
    def calculate_fantasy_points(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Calculate fantasy points for each player game/season.
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            DataFrame with added 'fantasy_points' column
        """
        df = df.clone()
        
        # Initialize fantasy points column
        if "fantasy_points" not in df.columns:
            df = df.with_columns(pl.lit(0.0).alias("fantasy_points"))
        
        # Calculate passing points
        if "passing_yards" in df.columns:
            df = df.with_columns(
                (pl.col("passing_yards") * self.scoring.get("passing_yards", 0.04))
                .alias("passing_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("passing_fp"))
        
        if "passing_tds" in df.columns:
            df = df.with_columns(
                (pl.col("passing_tds") * self.scoring.get("passing_tds", 4))
                .alias("passing_td_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("passing_td_fp"))
        
        if "interceptions" in df.columns:
            df = df.with_columns(
                (pl.col("interceptions") * self.scoring.get("interceptions", -2))
                .alias("int_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("int_fp"))
        
        # Calculate rushing points
        if "rushing_yards" in df.columns:
            df = df.with_columns(
                (pl.col("rushing_yards") * self.scoring.get("rushing_yards", 0.1))
                .alias("rushing_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("rushing_fp"))
        
        if "rushing_tds" in df.columns:
            df = df.with_columns(
                (pl.col("rushing_tds") * self.scoring.get("rushing_tds", 6))
                .alias("rushing_td_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("rushing_td_fp"))
        
        # Calculate receiving points
        if "receptions" in df.columns:
            df = df.with_columns(
                (pl.col("receptions") * self.scoring.get("receptions", 0.5))
                .alias("rec_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("rec_fp"))
        
        if "receiving_yards" in df.columns:
            df = df.with_columns(
                (pl.col("receiving_yards") * self.scoring.get("receiving_yards", 0.1))
                .alias("receiving_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("receiving_fp"))
        
        if "receiving_tds" in df.columns:
            df = df.with_columns(
                (pl.col("receiving_tds") * self.scoring.get("receiving_tds", 6))
                .alias("receiving_td_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("receiving_td_fp"))
        
        # Calculate fumble points
        if "fumbles_lost" in df.columns:
            df = df.with_columns(
                (pl.col("fumbles_lost") * self.scoring.get("fumbles_lost", -2))
                .alias("fumble_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("fumble_fp"))
        
        # Calculate two-point conversion points
        if "two_point_conversions" in df.columns:
            df = df.with_columns(
                (pl.col("two_point_conversions") * self.scoring.get("two_point_conversions", 2))
                .alias("two_pt_fp")
            )
        else:
            df = df.with_columns(pl.lit(0.0).alias("two_pt_fp"))
        
        # Sum all fantasy points
        df = df.with_columns(
            (
                pl.col("passing_fp")
                + pl.col("passing_td_fp")
                + pl.col("int_fp")
                + pl.col("rushing_fp")
                + pl.col("rushing_td_fp")
                + pl.col("rec_fp")
                + pl.col("receiving_fp")
                + pl.col("receiving_td_fp")
                + pl.col("fumble_fp")
                + pl.col("two_pt_fp")
            ).alias("fantasy_points")
        )
        
        return df
    
    def get_position_scoring_columns(self, position: str) -> list:
        """
        Get the relevant scoring columns for a position.
        
        Args:
            position: Player position (QB, RB, WR, TE)
            
        Returns:
            List of column names relevant for scoring
        """
        position_map = {
            "QB": ["passing_yards", "passing_tds", "interceptions", "rushing_yards", "rushing_tds"],
            "RB": ["rushing_yards", "rushing_tds", "receptions", "receiving_yards", "receiving_tds"],
            "WR": ["receptions", "receiving_yards", "receiving_tds", "rushing_yards", "rushing_tds"],
            "TE": ["receptions", "receiving_yards", "receiving_tds"],
        }
        
        return position_map.get(position.upper(), [])

