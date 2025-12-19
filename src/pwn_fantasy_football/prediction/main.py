"""Main entry point for fantasy predictions."""

import sys
import argparse
from pathlib import Path
import polars as pl

# Add src directory to path to allow running directly without installing the package
# Path structure: src/pwn_fantasy_football/prediction/main.py
# We need to go up 3 levels to get to src/
src_dir = Path(__file__).resolve().parent.parent.parent
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from pwn_fantasy_football.prediction.predictor import FantasyPredictor


def main():
    """Main function to generate predictions."""
    parser = argparse.ArgumentParser(
        description="Predict fantasy football performance for 2026 season"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration JSON file (default: cfg/cfg.json)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=None,
        help="Number of top players to display (default: from config)",
    )
    parser.add_argument(
        "--position",
        type=str,
        choices=["QB", "RB", "WR", "TE", "ALL"],
        default="ALL",
        help="Filter by position (default: ALL)",
    )
    
    args = parser.parse_args()
    
    # Initialize predictor
    config_path = args.config
    if config_path:
        config_path = Path(config_path)
    
    predictor = FantasyPredictor(config_path)
    
    # Generate predictions
    print("Generating fantasy football predictions for 2026...")
    predictions_df = predictor.predict_all_players()
    
    # Filter by position if specified
    if args.position != "ALL":
        # Ensure position is string before filtering
        predictions_df = predictions_df.with_columns(
            pl.col("position").map_elements(
                lambda x: x[0] if isinstance(x, list) and x else (str(x) if x is not None else "UNK"),
                return_dtype=pl.Utf8
            ).alias("position")
        )
        # Filter by position
        predictions_df = predictions_df.filter(pl.col("position") == args.position)
    
    # Check if we have any results
    if len(predictions_df) == 0:
        print(f"\nNo players found for position: {args.position}")
        print("Try running without --position filter or check your data.")
        return
    
    # Get top players
    top_n = args.top_n if args.top_n else None
    top_players = predictor.get_top_players(predictions_df, n=top_n)
    
    # Display results
    print(f"\n{'='*80}")
    print(f"TOP {len(top_players)} FANTASY PLAYERS FOR 2026")
    print(f"{'='*80}\n")
    
    if len(top_players) == 0:
        print("No players to display.")
        return
    
    for idx, row in enumerate(top_players.iter_rows(named=True), 1):
        # Handle position if it's a list
        position = row['position']
        if isinstance(position, list):
            position = position[0] if position else "UNK"
        position = str(position)
        
        print(f"{idx:3d}. {row['player_name']:30s} ({position:2s}) "
              f"| Predicted: {row['predicted_season_fp']:6.1f} FP "
              f"| Avg/Game: {row['predicted_avg_fp_per_game']:5.2f} "
              f"| Trend: {row['trend']:+.3f}")
    
    # Save predictions
    output_path = predictor.save_predictions(predictions_df)
    print(f"\nFull predictions saved to: {output_path}")
    
    # Save top players summary
    if args.top_n or predictor.config["output"].get("top_n_players"):
        summary_path = output_path.parent / f"top_players_2026.csv"
        # Ensure all columns are flat (no nested data) before writing CSV
        top_players_flat = top_players.with_columns([
            pl.col("position").map_elements(
                lambda x: x[0] if isinstance(x, list) and x else (str(x) if x is not None else "UNK"),
                return_dtype=pl.Utf8
            ).alias("position")
        ])
        top_players_flat.write_csv(summary_path)
        print(f"Top players summary saved to: {summary_path}")


if __name__ == "__main__":
    main()

