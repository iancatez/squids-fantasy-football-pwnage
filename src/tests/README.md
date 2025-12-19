# Tests

This directory contains comprehensive tests for the `pwn_fantasy_football` project.

## Test Structure

```
src/tests/
├── conftest.py           # Shared fixtures and test configuration
├── test_utils.py         # Tests for utility functions
├── test_data_fetcher.py  # Tests for NFLDataFetcher class
├── test_main.py          # Tests for CLI interface
└── README.md            # This file
```

## Modules Tested

- **data_fetch**: Data fetching utilities and NFLDataFetcher class
- **prediction**: (Tests coming soon)

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest src/tests/test_utils.py
pytest src/tests/test_data_fetcher.py
pytest src/tests/test_main.py
```

### Run with Coverage

```bash
pytest --cov=pwn_fantasy_football --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test

```bash
pytest src/tests/test_utils.py::TestEnsureDirectory::test_create_new_directory
```

## Test Coverage

### `test_utils.py`

Tests for utility functions in `data_fetch.utils`:
- `ensure_directory()` - Directory creation and path handling
- `save_dataframe()` - Saving DataFrames in various formats (Parquet, CSV, JSON)
- `load_config()` - Configuration file loading
- `get_season_list()` - Season list generation
- `merge_dataframes()` - DataFrame concatenation

### `test_data_fetcher.py`

Tests for the `NFLDataFetcher` class:
- Initialization with default and custom configs
- Season list generation
- Individual fetch methods (player_stats, rosters, schedules, etc.)
- Disabled data type handling
- Error handling
- Output path generation
- `fetch_all()` method

### `test_main.py`

Tests for the CLI interface:
- Command-line argument parsing
- Data type selection
- Season specification
- Custom configuration file handling

## Test Fixtures

Shared fixtures are defined in `conftest.py`:
- `temp_dir` - Temporary directory for test files
- `sample_config` - Sample configuration dictionary
- `config_file` - Temporary config file
- `sample_polars_df` - Sample Polars DataFrame
- `sample_pandas_df` - Sample Pandas DataFrame
- `mock_nflreadpy` - Mocked nflreadpy module

## Writing New Tests

When adding new functionality, follow these guidelines:

1. **Use fixtures** from `conftest.py` when possible
2. **Mock external dependencies** (like nflreadpy) to avoid network calls
3. **Test both success and failure cases**
4. **Use descriptive test names** that explain what is being tested
5. **Group related tests** in classes

### Example Test Structure

```python
class TestNewFeature:
    """Tests for new feature."""
    
    def test_basic_functionality(self, fixture):
        """Test basic functionality."""
        # Arrange
        # Act
        # Assert
        pass
    
    def test_error_handling(self, fixture):
        """Test error handling."""
        with pytest.raises(ExpectedError):
            # code that raises error
            pass
```

## Continuous Integration

Tests should pass before merging code. The project uses:
- **pytest** for test execution
- **pytest-cov** for coverage reporting
- **pytest** configuration in `pyproject.toml`

## Notes

- Tests use mocking to avoid actual network calls or file system operations where possible
- Temporary directories are used for file-based tests
- All tests should be independent and not rely on execution order

