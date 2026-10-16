$ErrorActionPreference = "Stop"

$pgCtl = "C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe"
$pgIsReady = "C:\Program Files\PostgreSQL\16\bin\pg_isready.exe"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$dataDir = Join-Path $projectRoot "database\postgres_data"

if (-not (Test-Path -LiteralPath $pgCtl)) {
    throw "PostgreSQL 16 was not found at $pgCtl"
}
if (-not (Test-Path -LiteralPath $dataDir)) {
    throw "The Drake PostgreSQL data directory is missing: $dataDir"
}

& $pgIsReady -h 127.0.0.1 -p 5543 -d drake_ai -U drake *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Output "Drake PostgreSQL is already stopped."
    exit 0
}

& $pgCtl -D $dataDir stop -m fast
if ($LASTEXITCODE -ne 0) {
    throw "PostgreSQL failed to stop cleanly."
}

