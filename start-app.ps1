$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Create .venv and install requirements.txt first."
}
& "$PSScriptRoot\start-postgres.ps1"
& $python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8053 --server.headless true --browser.gatherUsageStats false
