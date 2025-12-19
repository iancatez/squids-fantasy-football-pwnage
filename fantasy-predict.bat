@echo off
REM Fantasy Football Prediction - Windows Batch Wrapper
REM This provides a simple command-line interface for Windows

setlocal

REM Get the script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%

REM Default values
set TOP_N=
set POSITION=
set TARGET_SEASON=2026
set QUICK=
set FORCE_REFRESH=
set CACHE_DURATION=24
set DATA_DIR=
set NO_SAVE=
set VERBOSE=

REM Parse arguments
:parse_args
if "%~1"=="" goto end_parse
if /i "%~1"=="--top-n" (
    set TOP_N=--top-n %~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--position" (
    set POSITION=--position %~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--target-season" (
    set TARGET_SEASON=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--quick" (
    set QUICK=--quick
    shift
    goto parse_args
)
if /i "%~1"=="--force-refresh" (
    set FORCE_REFRESH=--force-refresh
    shift
    goto parse_args
)
if /i "%~1"=="--cache-duration-hours" (
    set CACHE_DURATION=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--data-dir" (
    set DATA_DIR=--data-dir %~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--no-save" (
    set NO_SAVE=--no-save
    shift
    goto parse_args
)
if /i "%~1"=="--verbose" (
    set VERBOSE=--verbose
    shift
    goto parse_args
)
if /i "%~1"=="--help" (
    echo Fantasy Football Prediction System
    echo.
    echo Usage: fantasy-predict.bat [options]
    echo.
    echo Options:
    echo   --top-n N              Number of top players (default: all)
    echo   --position POS         Filter by position: QB, RB, WR, TE, ALL
    echo   --target-season YEAR   Target season (default: 2026)
    echo   --quick                Quick predict mode (top 20, all positions)
    echo   --force-refresh        Force data refresh
    echo   --cache-duration-hours HOURS  Max age before refresh (default: 24)
    echo   --data-dir DIR         Data directory (default: ./data_output)
    echo   --no-save              Don't save predictions
    echo   --verbose               Verbose output
    echo   --help                 Show this help
    echo.
    echo Examples:
    echo   fantasy-predict.bat --top-n 30 --position QB
    echo   fantasy-predict.bat --quick
    echo   fantasy-predict.bat --position RB --force-refresh
    exit /b 0
)
shift
goto parse_args

:end_parse

REM Execute Python script
echo Executing Fantasy Football Prediction...
echo.

python -m pwn_fantasy_football.cli %TOP_N% %POSITION% --target-season %TARGET_SEASON% %QUICK% %FORCE_REFRESH% --cache-duration-hours %CACHE_DURATION% %DATA_DIR% %NO_SAVE% %VERBOSE%

endlocal

