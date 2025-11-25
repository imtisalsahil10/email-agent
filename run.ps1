<#
Helpers to run the Streamlit UI for this project in Windows PowerShell.

Usage (run from repo root):
  .\run.ps1

What it does:
- Activates the project's .venv (if present)
- Launches `streamlit run app.py` using the venv
- Falls back to `python -m streamlit run app.py` if the CLI is not present on PATH
#>

param(
    [switch]$NoActivate  # if supplied, skip activation and run directly via python -m
)

function Start-Streamlit {
    param($pythonExe)
    Write-Host "Starting Streamlit with: $pythonExe -m streamlit run app.py" -ForegroundColor Cyan
    & $pythonExe -m streamlit run app.py
}

try {
    $repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    Push-Location $repoRoot

    $venvPath = Join-Path $repoRoot '.venv\Scripts\Activate.ps1'
    $pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'

    if (-not $NoActivate) {
        if (Test-Path $venvPath) {
            try {
                Write-Host "Activating .venv..." -ForegroundColor Green
                & $venvPath
            } catch {
                # Avoid special unicode characters and embedded quotes that can confuse older PowerShell parsers
                $msg = "Failed to run Activate.ps1 - attempting python -m streamlit instead."
                Write-Warning ($msg + " " + $_.ToString())
            }
        }
    }

    # Prefer streamlit on PATH (activated venv would provide it). If not available, use python -m streamlit.
    $streamlitFound = Get-Command streamlit -ErrorAction SilentlyContinue
    if ($streamlitFound) {
        Write-Host "Running streamlit run app.py..." -ForegroundColor Cyan
        streamlit run app.py
    } else {
        if (Test-Path $pythonExe) {
            Start-Streamlit -pythonExe $pythonExe
        } else {
            $errMsg = "Couldn't find a Streamlit binary or the venv python. Make sure .venv exists and run: python -m venv .venv  && pip install -r requirements.txt before trying again."
            Write-Error $errMsg
            exit 2
        }
    }
} finally {
    Pop-Location -ErrorAction SilentlyContinue
}
