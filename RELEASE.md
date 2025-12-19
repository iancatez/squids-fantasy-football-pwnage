# Release Notes - v0.1.0

**Release Date:** January 2025  
**Version:** 0.1.0  
**Status:** Initial Release

## Overview

This is the initial release of **Squids Fantasy Football Pwnage**, a comprehensive fantasy football prediction and data analysis tool. This release provides a complete system for fetching historical NFL data and generating statistical predictions for fantasy football players.

## What's New

### 🎯 Core Features

#### Data Fetching Module (`data_fetch/`)
- **Comprehensive NFL Data Collection**: Fetch multiple types of NFL data including:
  - Player game-level statistics
  - Player seasonal and weekly statistics
  - Team statistics
  - Rosters, schedules, and injuries
  - Draft picks and contracts
  - Play-by-play data (optional, large dataset)

- **Smart Caching System**: 
  - Filesystem-based caching to minimize redundant downloads
  - Configurable cache duration (default: 24 hours)
  - Automatic cache management

- **Multiple Output Formats**: 
  - Parquet (default, optimized for ML workflows)
  - CSV (human-readable)
  - JSON (for web applications)

- **Configurable via JSON**: All parameters controlled through `cfg.json` files

#### Prediction Module (`prediction/`)
- **Statistical Prediction Algorithm**: 
  - Weighted recent performance analysis (more recent seasons weighted higher)
  - Trend detection (identifying improving/declining players)
  - Consistency scoring (rewarding reliable players)
  - Full season projections (17-game season)

- **Fantasy Point Calculation**: 
  - Standard scoring system (configurable)
  - Support for all major scoring categories
  - Customizable scoring rules via config

- **Position Filtering**: 
  - Filter predictions by QB, RB, WR, TE
  - Position-specific analysis

- **Comprehensive Output**: 
  - Detailed prediction metrics
  - Top N player rankings
  - Multiple output formats

#### Unified Interface (`__init__.py`)
- **CMDlet-Style Interface**: 
  - Single function call handles data fetching and predictions
  - Automatic data freshness checking
  - Smart cache management
  - Force refresh option

- **Python API**: 
  - `predict_fantasy_players()` - Main unified function
  - `quick_predict()` - Convenience function with defaults
  - Full programmatic access to all features

#### Command-Line Interface (`cli.py`)
- **Multiple Interface Options**:
  - Python module: `python -m pwn_fantasy_football.cli`
  - PowerShell script: `Invoke-FantasyPredict.ps1`
  - Windows batch file: `fantasy-predict.bat`
  - Installed command: `fantasy-predict` (after installation)

- **Comprehensive Options**:
  - Position filtering
  - Top N selection
  - Force refresh
  - Custom cache duration
  - Verbose output
  - Configuration file support

#### Testing Suite (`tests/`)
- **Comprehensive Test Coverage**:
  - Unit tests for utility functions
  - Tests for data fetcher class
  - CLI interface tests
  - Mocked external dependencies
  - Isolated test fixtures

## Installation

### Prerequisites

- Python >= 3.8
- pip package manager
- Internet connection (for data fetching)

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd squids-fantasy-football-pwnage

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Dependencies

Key dependencies:
- `nflreadpy>=0.1.5` - NFL data access
- `polars>=1.36.1` - Fast DataFrame operations
- `pandas>=2.3.3` - Data manipulation (alternative to Polars)
- `tqdm>=4.67.1` - Progress bars

See `requirements.txt` for complete list.

## Quick Start

### Option 1: Unified Interface (Recommended)

```python
from pwn_fantasy_football import predict_fantasy_players

# Automatically fetches data if needed, then generates predictions
results = predict_fantasy_players(
    top_n=30,
    position="QB",
    target_season=2026
)

print(results['top_players'])
```

### Option 2: Command Line

```bash
# Get top 30 QBs
python -m pwn_fantasy_football.cli --top-n 30 --position QB

# Quick predict (top 20, all positions)
python -m pwn_fantasy_football.cli --quick
```

### Option 3: PowerShell (Windows)

```powershell
.\Invoke-FantasyPredict.ps1 -TopN 30 -Position QB
```

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
│       │   └── README.md        # Documentation
│       ├── prediction/          # Prediction module
│       │   ├── cfg/             # Prediction configuration
│       │   ├── predictor.py     # Main prediction algorithm
│       │   ├── fantasy_calculator.py # Fantasy point calculator
│       │   ├── main.py          # CLI interface
│       │   ├── example_usage.py # Usage examples
│       │   └── README.md        # Documentation
│       ├── __init__.py          # Unified interface
│       ├── cli.py               # Command-line interface
│       └── example_usage.py     # Package-level examples
├── src/tests/                   # Test suite
│   ├── conftest.py             # Shared fixtures
│   ├── test_utils.py           # Utility tests
│   ├── test_data_fetcher.py    # Data fetcher tests
│   ├── test_main.py            # CLI tests
│   └── README.md               # Test documentation
├── data_output/                 # Fetched data (generated)
├── data_cache/                  # Cache directory (generated)
├── predictions/                 # Prediction outputs (generated)
├── README.md                    # Main documentation
├── USAGE.md                     # Usage guide
├── RELEASE.md                   # This file
├── requirements.txt             # Python dependencies
└── pyproject.toml               # Project configuration
```

## Key Features in Detail

### Automatic Data Management

The unified interface automatically:
1. Checks if player statistics data exists
2. Verifies data freshness (based on cache duration)
3. Fetches missing or stale data
4. Caches data for future use
5. Generates predictions

No manual data fetching required!

### Statistical Prediction Algorithm

The prediction algorithm uses a multi-factor approach:

1. **Weighted Recent Average**: Recent seasons (last 3 years) are weighted more heavily
2. **Trend Analysis**: Linear regression to identify improving/declining players
3. **Consistency Scoring**: Players with lower variance get a bonus
4. **Season Projection**: Projects average per-game performance to full 17-game season

Formula:
```
Predicted FP = Weighted Recent Average + (Trend × Trend Weight) + (Consistency × Consistency Weight)
```

### Configuration

All modules are highly configurable via JSON files:

- **Data Fetching**: `src/pwn_fantasy_football/data_fetch/cfg/cfg.json`
  - Season ranges
  - Data type enable/disable
  - Output formats
  - Cache settings
  - HTTP settings

- **Predictions**: `src/pwn_fantasy_football/prediction/cfg/cfg.json`
  - Fantasy scoring rules
  - Prediction parameters (weights, filters)
  - Output settings

## Documentation

Comprehensive documentation is available:

- **Main README.md**: Project overview and quick start
- **USAGE.md**: Detailed usage guide for end users
- **data_fetch/README.md**: Complete data fetching documentation
- **prediction/README.md**: Prediction algorithm documentation
- **tests/README.md**: Testing documentation

## Examples

### Example 1: Top Quarterbacks

```bash
python -m pwn_fantasy_football.cli --top-n 30 --position QB
```

### Example 2: Force Refresh Data

```bash
python -m pwn_fantasy_football.cli --top-n 20 --position RB --force-refresh
```

### Example 3: Custom Cache Duration

```bash
python -m pwn_fantasy_football.cli --position WR --cache-duration-hours 12
```

### Example 4: Python API

```python
from pwn_fantasy_football import predict_fantasy_players

results = predict_fantasy_players(
    top_n=30,
    position="QB",
    target_season=2026,
    cache_duration_hours=24,
    force_refresh=False
)

# Access results
top_players = results['top_players']
summary = results['summary']
print(f"Found {summary['total_players']} players")
```

## Known Limitations

1. **No ML Models**: This release uses pure statistical analysis, not machine learning
2. **Rookie Players**: Requires minimum 2 seasons of data (configurable)
3. **No Context Factors**: Doesn't account for:
   - Team changes
   - Coaching changes
   - Injuries (beyond historical data)
   - Schedule strength
   - Matchup analysis
4. **Fixed Season Length**: Assumes 17-game season projection
5. **Data Dependency**: Requires internet connection for initial data fetch

## Performance

- **First Run**: May take several minutes to download historical data (2010-2024)
- **Subsequent Runs**: Fast (uses cached data)
- **Data Size**: Player stats data ~100-500MB depending on seasons fetched
- **Prediction Speed**: Generates predictions for hundreds of players in seconds

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pwn_fantasy_football --cov-report=html

# Run specific test file
pytest src/tests/test_utils.py
```

## Breaking Changes

N/A - This is the initial release.

## Migration Guide

N/A - This is the initial release.

## Roadmap

Future enhancements planned:

- [ ] Machine learning prediction models
- [ ] Rookie player predictions
- [ ] Team/coaching factor integration
- [ ] Injury risk assessment
- [ ] Schedule strength adjustments
- [ ] Matchup analysis
- [ ] Advanced analytics dashboard
- [ ] Web interface (optional)
- [ ] Real-time data updates
- [ ] Multi-league scoring support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For questions or issues:
1. Check the documentation (README.md, USAGE.md, module READMEs)
2. Review example usage files
3. Open an issue on GitHub

## Credits

- **Author**: Ian Cates
- **Data Source**: [nflreadpy](https://nflreadpy.nflverse.com/) / [nflverse](https://www.nflverse.com/)
- **Built with**: Python, Polars, nflreadpy

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0 (Initial Release)

**Added:**
- Data fetching module with comprehensive NFL data collection
- Statistical prediction algorithm
- Unified CMDlet-style interface
- Command-line interfaces (Python, PowerShell, Batch)
- Comprehensive test suite
- Full documentation suite
- Example usage files
- Configuration system
- Smart caching system
- Multiple output formats

**Features:**
- Automatic data management
- Position filtering
- Top N player selection
- Force refresh option
- Custom cache duration
- Verbose output
- Configuration file support

---

**Happy Fantasy Football Pwnage! 🏈**

For detailed usage instructions, see [USAGE.md](USAGE.md).  
For project overview, see [README.md](README.md).

