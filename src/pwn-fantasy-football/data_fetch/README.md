# Data Fetch Module

This module provides a comprehensive system for fetching NFL historical data using the `nflreadpy` library. It's designed to build datasets for machine learning model training by collecting player statistics, team data, rosters, schedules, and more.

## Features

- **Comprehensive Data Collection**: Fetch multiple types of NFL data including:
  - Player game-level statistics
  - Player seasonal statistics
  - Player weekly statistics
  - Team statistics
  - Rosters
  - Schedules
  - Injuries
  - Draft picks
  - Contracts
  - Play-by-play data (optional, large dataset)

- **Configurable**: All parameters are configurable via `cfg/cfg.json`
- **Efficient Caching**: Built-in filesystem caching to avoid redundant downloads
- **Multiple Output Formats**: Support for Parquet (default), CSV, and JSON
- **Error Handling**: Robust error handling with logging
- **Progress Tracking**: Visual progress bars for long-running fetches

## Quick Start

### Basic Usage

Fetch all enabled data types using default configuration:

```python
from pwn_fantasy_football.data_fetch import fetch_all_data

fetch_all_data()
```

### Using the NFLDataFetcher Class

For more control, use the `NFLDataFetcher` class directly:

```python
from pwn_fantasy_football.data_fetch import NFLDataFetcher

# Initialize with default config
fetcher = NFLDataFetcher()

# Fetch specific data types
fetcher.fetch_player_stats()
fetcher.fetch_rosters()
fetcher.fetch_schedules()

# Or fetch everything
fetcher.fetch_all()
```

### Fetching Specific Seasons

```python
from pwn_fantasy_football.data_fetch import NFLDataFetcher

fetcher = NFLDataFetcher()

# Fetch only 2022 and 2023 seasons
seasons = [2022, 2023]
fetcher.fetch_player_stats(seasons=seasons)
fetcher.fetch_all(seasons=seasons)
```

### Command Line Interface

You can also use the command-line interface:

```bash
# Fetch all data types
python -m pwn_fantasy_football.data_fetch.main --data-type all

# Fetch only player stats
python -m pwn_fantasy_football.data_fetch.main --data-type player_stats

# Fetch specific seasons
python -m pwn_fantasy_football.data_fetch.main --data-type player_stats --seasons 2022 2023

# Use custom config file
python -m pwn_fantasy_football.data_fetch.main --config path/to/config.json
```

## Configuration

The configuration file (`cfg/cfg.json`) controls all aspects of data fetching:

### Season Configuration

```json
{
  "seasons": {
    "start_year": 2010,
    "end_year": 2024,
    "include_current": true
  }
}
```

### Data Types

Enable or disable specific data types:

```json
{
  "data_types": {
    "player_stats": {
      "enabled": true,
      "format": "parquet"
    },
    "play_by_play": {
      "enabled": false,
      "format": "parquet",
      "note": "Large dataset, enable only if needed"
    }
  }
}
```

### Cache Settings

```json
{
  "cache": {
    "mode": "filesystem",
    "directory": "./data_cache",
    "duration": 86400,
    "verbose": true
  }
}
```

### Output Settings

```json
{
  "output": {
    "directory": "./data_output",
    "format": "parquet",
    "create_subdirectories": true,
    "compression": "snappy"
  }
}
```

## Available Data Types

| Data Type | Method | Description |
|-----------|--------|-------------|
| Player Stats | `fetch_player_stats()` | Game-level player statistics |
| Player Seasonal | `fetch_player_seasonal()` | Seasonal aggregated player stats |
| Player Weekly | `fetch_player_weekly()` | Weekly player statistics |
| Team Stats | `fetch_team_stats()` | Team-level statistics |
| Rosters | `fetch_rosters()` | Team rosters by season |
| Schedules | `fetch_schedules()` | Game schedules |
| Injuries | `fetch_injuries()` | Player injury reports |
| Draft Picks | `fetch_draft_picks()` | NFL draft data |
| Contracts | `fetch_contracts()` | Player contract information |
| Play-by-Play | `fetch_play_by_play()` | Detailed play-by-play data (large) |

## Output Structure

By default, data is saved to `./data_output/` with the following structure:

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

If `create_subdirectories` is set to `false`, all files are saved directly in the output directory.

## Examples

See `example_usage.py` for more detailed examples of different usage patterns.

### Example 1: Fetch Only Recent Seasons

```python
from pwn_fantasy_football.data_fetch import NFLDataFetcher

fetcher = NFLDataFetcher()
recent_seasons = [2020, 2021, 2022, 2023, 2024]
fetcher.fetch_player_stats(seasons=recent_seasons)
```

### Example 2: Custom Configuration

```python
from pathlib import Path
from pwn_fantasy_football.data_fetch import NFLDataFetcher

custom_config = Path("path/to/custom_config.json")
fetcher = NFLDataFetcher(config_path=custom_config)
fetcher.fetch_all()
```

### Example 3: Selective Data Fetching

```python
from pwn_fantasy_football.data_fetch import NFLDataFetcher

fetcher = NFLDataFetcher()

# Only fetch what you need for your ML model
fetcher.fetch_player_stats()
fetcher.fetch_rosters()
fetcher.fetch_injuries()
```

## Data Formats

The module supports multiple output formats:

- **Parquet** (default): Efficient columnar format, best for ML workflows
- **CSV**: Human-readable, easy to inspect
- **JSON**: Good for web applications

Change the format in `cfg.json` or per data type:

```json
{
  "data_types": {
    "player_stats": {
      "format": "csv"
    }
  }
}
```

## Caching

The module uses filesystem caching to avoid redundant downloads. Cached data is stored in `./data_cache/` by default. The cache duration is configurable (default: 24 hours).

To clear the cache, simply delete the cache directory or set `cache_mode` to `"off"` in the config.

## Error Handling

The module includes comprehensive error handling:

- Missing functions in `nflreadpy` are handled gracefully
- Individual data type failures don't stop the entire fetch process
- Detailed logging helps diagnose issues
- Progress is saved even if some fetches fail

## Performance Tips

1. **Start Small**: Test with a few seasons before fetching all historical data
2. **Disable Unused Data Types**: Set `enabled: false` for data you don't need
3. **Use Parquet Format**: More efficient than CSV for large datasets
4. **Enable Caching**: Reduces download time on subsequent runs
5. **Play-by-Play Data**: Only enable if needed - it's very large

## Requirements

- `nflreadpy>=0.1.5`
- `polars>=1.36.1` or `pandas>=2.3.3`
- `tqdm` for progress bars

All dependencies are listed in the project's `requirements.txt`.

## Troubleshooting

### Issue: Function not found in nflreadpy

Some functions may not be available in all versions of `nflreadpy`. The module handles this gracefully by checking for function existence before calling. If a function is missing, you'll see a warning message and that data type will be skipped.

### Issue: Out of Memory

For very large datasets (especially play-by-play), consider:
- Fetching fewer seasons at a time
- Using Parquet format with compression
- Increasing available memory
- Processing data in chunks

### Issue: Slow Downloads

- Enable caching to avoid re-downloading
- Reduce the number of seasons fetched at once
- Check your internet connection
- Consider fetching during off-peak hours