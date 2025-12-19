"""
Command-line interface for the unified fantasy football prediction system.

This provides a CMDlet-style interface that can be called from PowerShell or command line.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src to path for direct execution
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from pwn_fantasy_football import predict_fantasy_players, quick_predict


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fantasy Football Prediction System - Unified Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get top 30 QBs
  python -m pwn_fantasy_football.cli --top-n 30 --position QB
  
  # Get top 20 RBs with force refresh
  python -m pwn_fantasy_football.cli --top-n 20 --position RB --force-refresh
  
  # Get all WRs
  python -m pwn_fantasy_football.cli --position WR
  
  # Quick predict (top 20, all positions)
  python -m pwn_fantasy_football.cli --quick
        """
    )
    
    # Main arguments
    parser.add_argument(
        "--top-n",
        type=int,
        default=None,
        help="Number of top players to return (default: all)"
    )
    
    parser.add_argument(
        "--position",
        type=str,
        choices=["QB", "RB", "WR", "TE", "ALL"],
        default=None,
        help="Filter by position (QB, RB, WR, TE, or ALL for all positions)"
    )
    
    parser.add_argument(
        "--target-season",
        type=int,
        default=2026,
        help="Target season for predictions (default: 2026)"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use quick_predict with defaults (top 20, all positions)"
    )
    
    # Data management arguments
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force data refresh even if cached data is fresh"
    )
    
    parser.add_argument(
        "--cache-duration-hours",
        type=int,
        default=24,
        help="Maximum age in hours before data is considered stale (default: 24)"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Directory for data storage (default: ./data_output)"
    )
    
    # Configuration files
    parser.add_argument(
        "--data-fetch-config",
        type=str,
        default=None,
        help="Path to data_fetch configuration file"
    )
    
    parser.add_argument(
        "--prediction-config",
        type=str,
        default=None,
        help="Path to prediction configuration file"
    )
    
    # Output options
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save predictions to file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle quick mode
    if args.quick:
        print("=" * 80)
        print("QUICK PREDICT MODE - Top 20 Players (All Positions)")
        print("=" * 80)
        results = quick_predict(
            top_n=20,
            force_refresh=args.force_refresh,
            cache_duration_hours=args.cache_duration_hours,
            data_dir=args.data_dir,
        )
    else:
        # Normal mode
        print("=" * 80)
        print(f"FANTASY FOOTBALL PREDICTIONS - Season {args.target_season}")
        print("=" * 80)
        
        if args.position:
            print(f"Position Filter: {args.position}")
        if args.top_n:
            print(f"Top N: {args.top_n}")
        print()
        
        results = predict_fantasy_players(
            top_n=args.top_n,
            position=args.position if args.position != "ALL" else None,
            target_season=args.target_season,
            data_dir=args.data_dir,
            cache_duration_hours=args.cache_duration_hours,
            force_refresh=args.force_refresh,
            data_fetch_config=args.data_fetch_config,
            prediction_config=args.prediction_config,
            save_predictions=not args.no_save,
        )
    
    # Display results
    print("\n" + "=" * 80)
    print(f"TOP {len(results['top_players'])} FANTASY PLAYERS")
    print("=" * 80)
    print()
    
    if len(results['top_players']) == 0:
        print("No players found matching criteria.")
        return
    
    # Display top players
    for idx, row in enumerate(results['top_players'].iter_rows(named=True), 1):
        # Handle position if it's a list
        position = row['position']
        if isinstance(position, list):
            position = position[0] if position else "UNK"
        position = str(position)
        
        print(f"{idx:3d}. {row['player_name']:30s} ({position:2s}) "
              f"| Predicted: {row['predicted_season_fp']:6.1f} FP "
              f"| Avg/Game: {row['predicted_avg_fp_per_game']:5.2f} "
              f"| Trend: {row['trend']:+.3f}")
    
    # Display summary
    summary = results['summary']
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total players analyzed: {summary['total_players']}")
    print(f"Top N displayed: {summary['top_n']}")
    if summary.get('position_filter'):
        print(f"Position filter: {summary['position_filter']}")
    print(f"Processing time: {summary['processing_time_seconds']}s")
    if summary.get('data_age_hours') is not None:
        print(f"Data age: {summary['data_age_hours']:.1f} hours")
        print(f"Data fresh: {summary['data_fresh']}")
    if summary.get('max_predicted_fp'):
        print(f"Max predicted FP: {summary['max_predicted_fp']:.1f}")
        print(f"Min predicted FP: {summary['min_predicted_fp']:.1f}")
        print(f"Avg predicted FP: {summary['avg_predicted_fp']:.1f}")
    
    if results.get('output_path'):
        print(f"\nPredictions saved to: {results['output_path']}")
    
    print("=" * 80)


if __name__ == "__main__":
    main()

