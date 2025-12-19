"""
Example usage of the unified CMDlet-style interface.

This demonstrates how to use the main package interface for fetching data
and generating predictions in a single call.
"""

from pwn_fantasy_football import predict_fantasy_players, quick_predict


def example_1_basic_usage():
    """Basic usage - get top 20 players."""
    print("=" * 80)
    print("Example 1: Basic Usage - Top 20 Players")
    print("=" * 80)
    
    results = predict_fantasy_players(top_n=20)
    
    print(f"\nTop {results['summary']['top_n']} Players:")
    print("-" * 80)
    for idx, row in enumerate(results['top_players'].iter_rows(named=True), 1):
        print(f"{idx:3d}. {row['player_name']:30s} ({row['position']:2s}) "
              f"| Predicted: {row['predicted_season_fp']:6.1f} FP "
              f"| Avg/Game: {row['predicted_avg_fp_per_game']:5.2f} "
              f"| Trend: {row['trend']:+.3f}")
    
    print(f"\nSummary:")
    print(f"  Total players analyzed: {results['summary']['total_players']}")
    print(f"  Processing time: {results['summary']['processing_time_seconds']}s")
    print(f"  Data age: {results['summary']['data_age_hours']:.1f} hours")
    print(f"  Data fresh: {results['summary']['data_fresh']}")


def example_2_position_filter():
    """Filter by position - get top QBs."""
    print("\n" + "=" * 80)
    print("Example 2: Position Filter - Top 10 QBs")
    print("=" * 80)
    
    results = predict_fantasy_players(
        top_n=10,
        position="QB"
    )
    
    print(f"\nTop {results['summary']['top_n']} Quarterbacks:")
    print("-" * 80)
    for idx, row in enumerate(results['top_players'].iter_rows(named=True), 1):
        print(f"{idx:3d}. {row['player_name']:30s} "
              f"| Predicted: {row['predicted_season_fp']:6.1f} FP "
              f"| Avg/Game: {row['predicted_avg_fp_per_game']:5.2f}")


def example_3_force_refresh():
    """Force refresh data even if cached."""
    print("\n" + "=" * 80)
    print("Example 3: Force Refresh - Update Data")
    print("=" * 80)
    
    results = predict_fantasy_players(
        top_n=15,
        position="RB",
        force_refresh=True  # Force data refresh
    )
    
    print(f"\nTop {results['summary']['top_n']} Running Backs (with fresh data):")
    print("-" * 80)
    for idx, row in enumerate(results['top_players'].iter_rows(named=True), 1):
        print(f"{idx:3d}. {row['player_name']:30s} "
              f"| Predicted: {row['predicted_season_fp']:6.1f} FP")


def example_4_quick_predict():
    """Use the quick_predict convenience function."""
    print("\n" + "=" * 80)
    print("Example 4: Quick Predict - Convenience Function")
    print("=" * 80)
    
    # Quick predict with defaults (top 20, all positions)
    results = quick_predict(top_n=20, position="WR")
    
    print(f"\nTop {results['summary']['top_n']} Wide Receivers:")
    print("-" * 80)
    for idx, row in enumerate(results['top_players'].iter_rows(named=True), 1):
        print(f"{idx:3d}. {row['player_name']:30s} "
              f"| Predicted: {row['predicted_season_fp']:6.1f} FP "
              f"| Consistency: {row['consistency_score']:.2f}")


def example_5_custom_cache():
    """Use custom cache duration."""
    print("\n" + "=" * 80)
    print("Example 5: Custom Cache Duration")
    print("=" * 80)
    
    # Only refresh if data is older than 12 hours
    results = predict_fantasy_players(
        top_n=25,
        cache_duration_hours=12,  # Refresh if older than 12 hours
        position="TE"
    )
    
    print(f"\nTop {results['summary']['top_n']} Tight Ends:")
    print("-" * 80)
    for idx, row in enumerate(results['top_players'].iter_rows(named=True), 1):
        print(f"{idx:3d}. {row['player_name']:30s} "
              f"| Predicted: {row['predicted_season_fp']:6.1f} FP")


def example_6_all_players():
    """Get all players without top_n limit."""
    print("\n" + "=" * 80)
    print("Example 6: All Players - No Top N Limit")
    print("=" * 80)
    
    results = predict_fantasy_players(
        top_n=None,  # Get all players
        position="QB"
    )
    
    print(f"\nAll Quarterbacks ({results['summary']['total_players']} total):")
    print("-" * 80)
    print(f"  Max predicted FP: {results['summary']['max_predicted_fp']:.1f}")
    print(f"  Min predicted FP: {results['summary']['min_predicted_fp']:.1f}")
    print(f"  Avg predicted FP: {results['summary']['avg_predicted_fp']:.1f}")


if __name__ == "__main__":
    # Run examples
    try:
        example_1_basic_usage()
        example_2_position_filter()
        # Uncomment to test other examples:
        # example_3_force_refresh()
        # example_4_quick_predict()
        # example_5_custom_cache()
        # example_6_all_players()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

