<#
.SYNOPSIS
    Fantasy Football Prediction CMDlet - PowerShell wrapper

.DESCRIPTION
    This PowerShell script provides a CMDlet-style interface for the fantasy football
    prediction system. It automatically handles data fetching and predictions.

.PARAMETER TopN
    Number of top players to return (default: all)

.PARAMETER Position
    Filter by position: QB, RB, WR, TE, or ALL (default: all positions)

.PARAMETER TargetSeason
    Target season for predictions (default: 2026)

.PARAMETER Quick
    Use quick predict mode (top 20, all positions)

.PARAMETER ForceRefresh
    Force data refresh even if cached data is fresh

.PARAMETER CacheDurationHours
    Maximum age in hours before data is considered stale (default: 24)

.PARAMETER DataDir
    Directory for data storage (default: ./data_output)

.PARAMETER NoSave
    Don't save predictions to file

.PARAMETER Verbose
    Verbose output

.EXAMPLE
    .\Invoke-FantasyPredict.ps1 -TopN 30 -Position QB
    
    Get top 30 quarterbacks for 2026 season

.EXAMPLE
    .\Invoke-FantasyPredict.ps1 -TopN 20 -Position RB -ForceRefresh
    
    Get top 20 running backs, forcing data refresh

.EXAMPLE
    .\Invoke-FantasyPredict.ps1 -Quick
    
    Quick predict mode (top 20, all positions)

.EXAMPLE
    .\Invoke-FantasyPredict.ps1 -Position WR -CacheDurationHours 12
    
    Get all wide receivers, refresh if data older than 12 hours
#>

param(
    [int]$TopN = 0,
    [ValidateSet("QB", "RB", "WR", "TE", "ALL")]
    [string]$Position = "ALL",
    [int]$TargetSeason = 2026,
    [switch]$Quick,
    [switch]$ForceRefresh,
    [int]$CacheDurationHours = 24,
    [string]$DataDir = "",
    [switch]$NoSave,
    [switch]$Verbose
)

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir

# Build Python command
$PythonCmd = "python"
$ModulePath = Join-Path $ProjectRoot "src\pwn_fantasy_football\cli.py"

# Build arguments
$Args = @()

if ($Quick) {
    $Args += "--quick"
} else {
    if ($TopN -gt 0) {
        $Args += "--top-n"
        $Args += $TopN.ToString()
    }
    
    if ($Position -ne "ALL") {
        $Args += "--position"
        $Args += $Position
    }
    
    $Args += "--target-season"
    $Args += $TargetSeason.ToString()
}

if ($ForceRefresh) {
    $Args += "--force-refresh"
}

if ($CacheDurationHours -ne 24) {
    $Args += "--cache-duration-hours"
    $Args += $CacheDurationHours.ToString()
}

if ($DataDir -ne "") {
    $Args += "--data-dir"
    $Args += $DataDir
}

if ($NoSave) {
    $Args += "--no-save"
}

if ($Verbose) {
    $Args += "--verbose"
}

# Execute Python script
Write-Host "Executing Fantasy Football Prediction..." -ForegroundColor Cyan
Write-Host ""

& $PythonCmd -m pwn_fantasy_football.cli $Args

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: Command failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

