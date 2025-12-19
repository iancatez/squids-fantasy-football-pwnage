# Usage Guide - CMDlet Style Interface

This guide shows you how to use the fantasy football prediction system as an end user.

## Quick Start

### Option 1: Python Module (Recommended)

```bash
# Get top 30 QBs
python -m pwn_fantasy_football.cli --top-n 30 --position QB

# Get top 20 RBs
python -m pwn_fantasy_football.cli --top-n 20 --position RB

# Quick predict (top 20, all positions)
python -m pwn_fantasy_football.cli --quick

# Get all WRs
python -m pwn_fantasy_football.cli --position WR
```

### Option 2: PowerShell (Windows)

```powershell
# Get top 30 QBs
.\Invoke-FantasyPredict.ps1 -TopN 30 -Position QB

# Get top 20 RBs with force refresh
.\Invoke-FantasyPredict.ps1 -TopN 20 -Position RB -ForceRefresh

# Quick predict
.\Invoke-FantasyPredict.ps1 -Quick

# Get all WRs, refresh if older than 12 hours
.\Invoke-FantasyPredict.ps1 -Position WR -CacheDurationHours 12
```

### Option 3: Windows Batch File

```cmd
# Get top 30 QBs
fantasy-predict.bat --top-n 30 --position QB

# Get top 20 RBs
fantasy-predict.bat --top-n 20 --position RB

# Quick predict
fantasy-predict.bat --quick
```

### Option 4: Installed Command (After pip install -e .)

```bash
# After installing the package, you can use:
fantasy-predict --top-n 30 --position QB
```

## Command Options

### Main Options

- `--top-n N` - Number of top players to return (default: all)
- `--position POS` - Filter by position: `QB`, `RB`, `WR`, `TE`, or `ALL` (default: all)
- `--target-season YEAR` - Target season for predictions (default: 2026)
- `--quick` - Quick predict mode (top 20, all positions)

### Data Management

- `--force-refresh` - Force data refresh even if cached data is fresh
- `--cache-duration-hours HOURS` - Maximum age in hours before data is considered stale (default: 24)
- `--data-dir DIR` - Directory for data storage (default: ./data_output)

### Configuration

- `--data-fetch-config PATH` - Path to data_fetch configuration file
- `--prediction-config PATH` - Path to prediction configuration file

### Output

- `--no-save` - Don't save predictions to file
- `--verbose` - Verbose output
- `--help` - Show help message

## Examples

### Example 1: Top Quarterbacks

```bash
python -m pwn_fantasy_football.cli --top-n 30 --position QB
```

Output:
```
================================================================================
FANTASY FOOTBALL PREDICTIONS - Season 2026
================================================================================
Position Filter: QB
Top N: 30

[Data fetching/checking happens automatically...]

================================================================================
TOP 30 FANTASY PLAYERS
================================================================================

  1. Patrick Mahomes              (QB) | Predicted:  350.2 FP | Avg/Game:  20.6 | Trend: +0.123
  2. Josh Allen                    (QB) | Predicted:  345.8 FP | Avg/Game:  20.3 | Trend: +0.089
  ...
```

### Example 2: Force Refresh Data

```bash
python -m pwn_fantasy_football.cli --top-n 20 --position RB --force-refresh
```

This will:
1. Force refresh player statistics data (even if cached)
2. Generate predictions for top 20 running backs
3. Display results

### Example 3: Quick Predict

```bash
python -m pwn_fantasy_football.cli --quick
```

This is a convenience command that:
- Gets top 20 players
- All positions
- Uses default settings

### Example 4: Custom Cache Duration

```bash
python -m pwn_fantasy_football.cli --position WR --cache-duration-hours 12
```

This will:
- Get all wide receivers
- Only refresh data if it's older than 12 hours (instead of default 24)

### Example 5: All Players, No Save

```bash
python -m pwn_fantasy_football.cli --position TE --no-save
```

This will:
- Get all tight ends
- Display results but don't save to file

## How It Works

1. **Data Check**: The system automatically checks if player statistics data exists
2. **Freshness Check**: If data exists, it checks if it's fresh (based on cache duration)
3. **Data Fetch**: If data is missing or stale, it automatically fetches/updates it
4. **Prediction**: Generates fantasy predictions using the statistical algorithm
5. **Display**: Shows top players with detailed statistics
6. **Save**: Saves predictions to file (unless `--no-save` is used)

## First Time Use

On first use, the system will:
1. Download historical NFL player statistics (this may take a few minutes)
2. Cache the data for future use
3. Generate predictions
4. Display results

Subsequent uses will be much faster as data is cached.

## Troubleshooting

### Issue: "Player stats not found"

The system will automatically fetch data on first use. If you see this error:
- Check your internet connection
- Ensure you have write permissions in the project directory
- Try running with `--force-refresh`

### Issue: Slow first run

The first run downloads historical data (2010-2024 by default). This is normal and only happens once (or when cache expires).

### Issue: Permission errors

On Windows, you may need to run PowerShell as Administrator or adjust execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Python API Usage

You can also use the Python API directly:

```python
from pwn_fantasy_football import predict_fantasy_players

results = predict_fantasy_players(
    top_n=30,
    position="QB",
    target_season=2026
)

print(results['top_players'])
```

See the main README.md for more Python API examples.

