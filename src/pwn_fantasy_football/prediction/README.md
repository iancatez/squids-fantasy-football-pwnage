# Fantasy Football Prediction Module

This module provides a statistical algorithm to predict fantasy football player performance for the upcoming 2026 season. It uses historical data analysis without requiring machine learning libraries.

## Features

- **Fantasy Point Calculation**: Standard scoring system (configurable)
- **Statistical Analysis**: 
  - Weighted recent performance (more recent seasons weighted higher)
  - Trend analysis (identifying improving/declining players)
  - Consistency scoring (rewarding reliable players)
- **Position Filtering**: Filter predictions by QB, RB, WR, TE
- **Comprehensive Output**: Predictions saved in multiple formats

## Algorithm Overview

The prediction algorithm uses a multi-factor approach:

1. **Weighted Recent Average**: Recent seasons (last 3 years) are weighted more heavily than older data
2. **Trend Analysis**: Linear regression to identify players on upward or downward trajectories
3. **Consistency Bonus**: Players with lower variance in performance get a bonus
4. **Season Projection**: Projects average per-game performance to full 17-game season

### Formula

```
Predicted FP = Weighted Recent Average + (Trend × Trend Weight) + (Consistency × Consistency Weight)
```

## Quick Start

### Prerequisites

First, ensure you have fetched player statistics data:

```python
from pwn_fantasy_football.data_fetch import fetch_all_data

# Fetch player stats (or use CLI: python -m pwn_fantasy_football.data_fetch.main --data-type player_stats)
fetch_all_data()
```

### Basic Usage

```python
from pwn_fantasy_football.prediction import FantasyPredictor

# Initialize predictor (uses data_output/player_stats by default)
predictor = FantasyPredictor()

# Generate predictions
predictions_df = predictor.predict_all_players()

# Get top 20 players
top_20 = predictor.get_top_players(predictions_df, n=20)

# Save predictions
output_path = predictor.save_predictions(predictions_df)
```

### Command Line Interface

```bash
# Generate predictions for all players
python -m pwn_fantasy_football.prediction.main

# Get top 30 players
python -m pwn_fantasy_football.prediction.main --top-n 30

# Filter by position
python -m pwn_fantasy_football.prediction.main --position QB
python -m pwn_fantasy_football.prediction.main --position RB --top-n 20
```

## Configuration

Edit `cfg/cfg.json` to customize:

### Scoring System

```json
{
  "scoring": {
    "passing_yards": 0.04,
    "passing_tds": 4,
    "rushing_yards": 0.1,
    "rushing_tds": 6,
    "receptions": 0.5,
    "receiving_yards": 0.1,
    "receiving_tds": 6
  }
}
```

### Prediction Parameters

```json
{
  "prediction": {
    "target_season": 2026,
    "min_seasons_played": 2,
    "recent_seasons_weight": 1.5,
    "trend_weight": 0.3,
    "consistency_weight": 0.2
  }
}
```

## Output

Predictions are saved to `./predictions/` directory:

- `predictions_2026.parquet` - Full predictions for all players
- `top_players_2026.csv` - Summary of top N players

### Prediction Columns

- `player_id` - Unique player identifier
- `player_name` - Player name
- `position` - Player position (QB, RB, WR, TE)
- `predicted_avg_fp_per_game` - Predicted fantasy points per game
- `predicted_season_fp` - Predicted total fantasy points for season
- `recent_avg_fp` - Average FP from recent seasons
- `trend` - Performance trend (positive = improving)
- `consistency_score` - Consistency metric (higher = more consistent)
- `seasons_analyzed` - Number of seasons used in prediction
- `last_season` - Most recent season in data

## Examples

### Example 1: Top Players by Position

```python
from pwn_fantasy_football.prediction import FantasyPredictor
import polars as pl

predictor = FantasyPredictor()
predictions_df = predictor.predict_all_players()

# Top 10 QBs
qbs = predictions_df.filter(pl.col("position") == "QB").head(10)
print("Top 10 QBs:")
for row in qbs.iter_rows(named=True):
    print(f"{row['player_name']}: {row['predicted_season_fp']:.1f} FP")
```

### Example 2: Players with Positive Trends

```python
# Find players on the rise
rising_players = predictions_df.filter(
    pl.col("trend") > 0.5
).sort("predicted_season_fp", descending=True)

print("Players with strong upward trends:")
for row in rising_players.head(15).iter_rows(named=True):
    print(f"{row['player_name']} ({row['position']}): "
          f"Trend: {row['trend']:+.2f}, "
          f"Predicted: {row['predicted_season_fp']:.1f} FP")
```

### Example 3: Most Consistent Players

```python
# Find most consistent high performers
consistent = predictions_df.filter(
    (pl.col("consistency_score") > 0.7) &
    (pl.col("predicted_season_fp") > 150)
).sort("predicted_season_fp", descending=True)

print("Consistent high performers:")
for row in consistent.head(20).iter_rows(named=True):
    print(f"{row['player_name']}: {row['predicted_season_fp']:.1f} FP "
          f"(Consistency: {row['consistency_score']:.2f})")
```

## Requirements

- Historical player statistics data (from `data_fetch` module)
  - Run `data_fetch` first to generate `data_output/player_stats/player_stats.parquet`
- Polars for data processing
- JSON configuration file (`cfg/cfg.json`)

## Data Requirements

Before running predictions, ensure you have:
1. Fetched player statistics data using the `data_fetch` module
2. Data should be in `data_output/player_stats/player_stats.parquet` (or configured path)
3. Data should include columns: `player_id`, `player_name`, `position`, `season`, and statistical columns for fantasy point calculation

## Algorithm Details

### Weighted Average Calculation

Recent seasons are weighted exponentially:
- Most recent season: weight = 1.0 + (0.3 × 0) = 1.0
- 2nd most recent: weight = 1.0 + (0.3 × 1) = 1.3
- 3rd most recent: weight = 1.0 + (0.3 × 2) = 1.6

### Trend Calculation

Uses simple linear regression on average FP per game over seasons:
- Positive slope = improving player
- Negative slope = declining player
- Trend is multiplied by `trend_weight` and added to prediction

### Consistency Score

Calculated as: `1 / (standard_deviation + 1)`
- Lower variance = higher consistency score
- Consistency bonus applied to final prediction

## Limitations

- No ML models (pure statistical approach)
- Doesn't account for:
  - Team changes
  - Coaching changes
  - Injuries
  - Rookie players (requires min_seasons_played)
  - Schedule strength
- Assumes 17-game season projection

## Future Enhancements

- Add support for rookie predictions
- Incorporate team/coaching factors
- Add injury risk assessment
- Schedule strength adjustments
- Machine learning integration option

## Troubleshooting

### Error: "Player stats not found"

Make sure you've run the data_fetch module first:
```python
from pwn_fantasy_football.data_fetch import fetch_all_data
fetch_all_data()
```

### No predictions generated

- Check that you have sufficient historical data
- Reduce `min_seasons_played` in config if needed
- Verify position filters are enabled

### Predictions seem off

- Adjust weights in config (trend_weight, consistency_weight)
- Check that scoring system matches your league
- Verify data quality from data_fetch

