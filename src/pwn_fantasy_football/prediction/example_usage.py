"""Example usage of the fantasy prediction system."""

from pathlib import Path
from pwn_fantasy_football.prediction import FantasyPredictor


def example_basic_prediction():
    """Basic example: generate predictions for all players."""
    print("Generating fantasy predictions for 2026...")
    
    predictor = FantasyPredictor()
    predictions_df = predictor.predict_all_players()
    
    # Get top 20 players
    top_20 = predictor.get_top_players(predictions_df, n=20)
    
    print("\nTop 20 Fantasy Players for 2026:")
    print("=" * 80)
    for idx, row in enumerate(top_20.iter_rows(named=True), 1):
        print(f"{idx:2d}. {row['player_name']:30s} ({row['position']:2s}) - "
              f"{row['predicted_season_fp']:6.1f} FP")
    
    # Save predictions
    output_path = predictor.save_predictions(predictions_df)
    print(f"\nPredictions saved to: {output_path}")


def example_position_specific():
    """Example: predict for specific position."""
    predictor = FantasyPredictor()
    predictions_df = predictor.predict_all_players()
    
    # Filter to QBs only
    qbs = predictions_df.filter(
        predictions_df["position"] == "QB"
    ).head(10)
    
    print("\nTop 10 QBs for 2026:")
    print("=" * 80)
    for idx, row in enumerate(qbs.iter_rows(named=True), 1):
        print(f"{idx:2d}. {row['player_name']:30s} - "
              f"{row['predicted_season_fp']:6.1f} FP "
              f"(Trend: {row['trend']:+.2f})")


def example_custom_config():
    """Example: use custom configuration."""
    custom_config = Path(__file__).parent / "cfg" / "cfg.json"
    predictor = FantasyPredictor(config_path=custom_config)
    
    predictions_df = predictor.predict_all_players()
    top_players = predictor.get_top_players(predictions_df, n=30)
    
    print(f"\nTop 30 players (custom config):")
    for row in top_players.iter_rows(named=True):
        print(f"{row['player_name']:30s} ({row['position']:2s}): "
              f"{row['predicted_season_fp']:6.1f} FP")


if __name__ == "__main__":
    # Run the basic example
    example_basic_prediction()
    
    # Uncomment to try other examples:
    # example_position_specific()
    # example_custom_config()

