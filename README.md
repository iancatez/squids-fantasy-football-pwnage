# Squids Fantasy Football Pwnage

A comprehensive fantasy football prediction and data analysis tool built with Python. This project provides tools for fetching historical NFL data, building machine learning models, and making fantasy football predictions.

## Features

- **Data Fetching**: Comprehensive NFL data collection using `nflreadpy`
  - Player statistics (game-level, weekly, seasonal)
  - Team statistics
  - Rosters, schedules, injuries
  - Draft picks and contracts
  - Play-by-play data (optional)
- **Fantasy Predictions**: Statistical algorithm for predicting 2026 fantasy performance
  - Weighted recent performance analysis
  - Trend detection (improving/declining players)
  - Consistency scoring
  - Position-specific filtering
- **Machine Learning Ready**: Structured data output in Parquet format optimized for ML workflows
- **Configurable**: JSON-based configuration for all modules
- **Efficient Caching**: Built-in caching to minimize redundant downloads

## Project Structure

```
squids-fantasy-football-pwnage/
├── src/
│   └── pwn_fantasy_football/
│       ├── data_fetch/          # Data fetching module
│       │   ├── cfg/             # Configuration files
│       │   ├── data_fetcher.py  # Main data fetching class
│       │   ├── utils.py         # Utility functions
│       │   ├── main.py          # CLI interface
│       │   ├── example_usage.py # Usage examples
│       │   └── README.md        # Detailed data_fetch documentation
│       └── prediction/          # Prediction module
│           ├── cfg/             # Prediction configuration
│           ├── predictor.py      # Main prediction algorithm
│           ├── fantasy_calculator.py # Fantasy point calculator
│           ├── main.py          # CLI interface
│           ├── example_usage.py # Usage examples
│           └── README.md        # Detailed prediction documentation
├── src/tests/                   # Test suite
│   ├── test_utils.py
│   ├── test_data_fetcher.py
│   ├── test_main.py
│   └── README.md
├── data_output/                 # Fetched data (generated)
├── data_cache/                  # Cache directory (generated)
├── predictions/                 # Prediction outputs (generated)
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd squids-fantasy-football-pwnage
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install as a package:
```bash
pip install -e .
```

## Quick Start

### Fetching NFL Data

The easiest way to get started is to fetch all available NFL data:

```python
from pwn_fantasy_football.data_fetch import fetch_all_data

fetch_all_data()
```

This will download historical NFL data from 2010-2024 (configurable) and save it to `./data_output/` in Parquet format.

### Fetching Specific Data Types

For more control, use the `NFLDataFetcher` class:

```python
from pwn_fantasy_football.data_fetch import NFLDataFetcher

fetcher = NFLDataFetcher()

# Fetch only player statistics
fetcher.fetch_player_stats()

# Fetch specific seasons
fetcher.fetch_player_stats(seasons=[2022, 2023, 2024])
```

### Command Line Interface

You can also use the CLI:

```bash
# Fetch all data
python -m pwn_fantasy_football.data_fetch.main --data-type all

# Fetch only player stats for specific seasons
python -m pwn_fantasy_football.data_fetch.main --data-type player_stats --seasons 2022 2023
```

## Configuration

All data fetching parameters are configured in `src/pwn-fantasy-football/data_fetch/cfg/cfg.json`. Key settings include:

- **Seasons**: Define the range of seasons to fetch (default: 2010-2024)
- **Data Types**: Enable/disable specific data types
- **Output Format**: Choose between Parquet (default), CSV, or JSON
- **Caching**: Configure cache directory and duration
- **Output Directory**: Where to save fetched data

See [data_fetch/README.md](src/pwn_fantasy_football/data_fetch/README.md) for detailed configuration documentation.

## Available Data Types

The data fetching module can retrieve:

| Data Type | Description | Use Case |
|-----------|-------------|----------|
| Player Stats | Game-level player statistics | Performance analysis, feature engineering |
| Player Seasonal | Season-aggregated stats | Year-over-year comparisons |
| Player Weekly | Weekly performance data | Weekly prediction models |
| Team Stats | Team-level statistics | Team performance analysis |
| Rosters | Team rosters by season | Player-team relationships |
| Schedules | Game schedules | Context for predictions |
| Injuries | Injury reports | Availability predictions |
| Draft Picks | NFL draft data | Rookie analysis |
| Contracts | Player contracts | Salary cap considerations |
| Play-by-Play | Detailed play data | Advanced analytics (large dataset) |

## Data Output

By default, data is saved to `./data_output/` in Parquet format:

```
data_output/
├── player_stats/
│   └── player_stats.parquet
├── rosters/
│   └── rosters.parquet
├── schedules/
│   └── schedules.parquet
└── ...
```

### Loading Data for ML

```python
import polars as pl

# Load player stats
df = pl.read_parquet("./data_output/player_stats/player_stats.parquet")

# Explore the data
print(df.head())
print(df.schema)
```

## Modules

### Data Fetch (`data_fetch/`)

Comprehensive NFL data fetching system. See [data_fetch/README.md](src/pwn-fantasy-football/data_fetch/README.md) for complete documentation.

**Key Features:**
- Multiple data types support
- Configurable via JSON
- Efficient caching
- Progress tracking
- Error handling

### Prediction (`prediction/`)

Statistical fantasy football prediction system. See [prediction/README.md](src/pwn_fantasy_football/prediction/README.md) for complete documentation.

**Key Features:**
- Multi-factor prediction algorithm (weighted averages, trends, consistency)
- Standard fantasy scoring (configurable)
- Position filtering (QB, RB, WR, TE)
- Comprehensive output with detailed metrics

**Quick Example:**
```python
from pwn_fantasy_football.prediction import FantasyPredictor

predictor = FantasyPredictor()
predictions_df = predictor.predict_all_players()
top_20 = predictor.get_top_players(predictions_df, n=20)
```

Or via CLI:
```bash
python src/pwn_fantasy_football/prediction/main.py --top-n 30 --position QB
```

## Development

### Code Quality

The project uses:
- **Black**: Code formatting (line length: 100)
- **Ruff**: Linting
- **MyPy**: Type checking (optional)
- **Pytest**: Testing

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Requirements

- Python >= 3.8
- See `requirements.txt` for full dependency list

Key dependencies:
- `nflreadpy>=0.1.5` - NFL data access
- `polars>=1.36.1` - Fast DataFrame operations
- `pandas>=2.3.3` - Data manipulation (alternative to Polars)
- `tqdm>=4.67.1` - Progress bars

## Usage Examples

### Example 1: Build a Complete Dataset

```python
from pwn_fantasy_football.data_fetch import fetch_all_data

# Fetch all historical data
fetch_all_data()

# Data is now in ./data_output/ ready for ML training
```

### Example 2: Fetch Recent Seasons Only

```python
from pwn_fantasy_football.data_fetch import NFLDataFetcher

fetcher = NFLDataFetcher()
recent_seasons = [2020, 2021, 2022, 2023, 2024]

# Fetch only recent data
fetcher.fetch_player_stats(seasons=recent_seasons)
fetcher.fetch_rosters(seasons=recent_seasons)
```

### Example 3: Custom Configuration

```python
from pathlib import Path
from pwn_fantasy_football.data_fetch import NFLDataFetcher

# Use a custom config file
custom_config = Path("path/to/custom_config.json")
fetcher = NFLDataFetcher(config_path=custom_config)
fetcher.fetch_all()
```

### Example 4: Generate Fantasy Predictions

```python
from pwn_fantasy_football.prediction import FantasyPredictor

# Generate predictions for 2026 season
predictor = FantasyPredictor()
predictions_df = predictor.predict_all_players()

# Get top 20 players
top_20 = predictor.get_top_players(predictions_df, n=20)

# Filter by position
qbs = predictions_df.filter(predictions_df["position"] == "QB").head(10)

# Save predictions
output_path = predictor.save_predictions(predictions_df)
```

## Performance Tips

1. **Start Small**: Test with a few seasons before fetching all historical data
2. **Use Parquet**: More efficient than CSV for large datasets
3. **Enable Caching**: Reduces download time on subsequent runs
4. **Selective Fetching**: Only fetch data types you need
5. **Play-by-Play**: Only enable if needed - it's a very large dataset

## Troubleshooting

### Common Issues

**Issue**: Function not found in nflreadpy
- **Solution**: The module handles missing functions gracefully. Check logs for warnings.

**Issue**: Out of memory
- **Solution**: Fetch fewer seasons at a time or use chunked processing.

**Issue**: Slow downloads
- **Solution**: Enable caching, reduce season range, or fetch during off-peak hours.

For more troubleshooting help, see:
- [data_fetch/README.md](src/pwn_fantasy_football/data_fetch/README.md) for data fetching issues
- [prediction/README.md](src/pwn_fantasy_football/prediction/README.md) for prediction issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Author

Ian Cates

## Acknowledgments

- Built using [nflreadpy](https://nflreadpy.nflverse.com/) for NFL data access
- Data provided by the nflverse project

## Roadmap

- [x] Data fetching module
- [x] Statistical prediction algorithm
- [ ] Machine learning prediction models
- [ ] Feature engineering utilities
- [ ] Model evaluation tools
- [ ] Advanced analytics (schedule strength, matchups)
- [ ] Web interface (optional)

## Support

For questions or issues:
1. Check the module-specific READMEs:
   - [data_fetch README](src/pwn_fantasy_football/data_fetch/README.md)
   - [prediction README](src/pwn_fantasy_football/prediction/README.md)
   - [tests README](src/tests/README.md)
2. Review the example usage files in each module
3. Open an issue on GitHub

---

**Happy Fantasy Football Pwnage! 🏈**
