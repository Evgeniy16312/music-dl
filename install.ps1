# One-time setup after cloning music-dl (Windows PowerShell)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

Write-Host "=== music-dl installer ===" -ForegroundColor Cyan

try {
    $pyVersion = python --version 2>&1
    Write-Host "Python: $pyVersion"
} catch {
    Write-Error @"
Python not found. Install Python 3.10+ from https://www.python.org/downloads/
During install, check "Add python.exe to PATH".
"@
}

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r "$Root\requirements.txt"
python -m pip install -e "$Root"

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. python ym_download.py auth          # login (once)"
Write-Host '  2. .\ym.ps1 "https://music.yandex.ru/album/12345"'
Write-Host ""
Write-Host "Or copy link to clipboard and run:  .\ym.ps1"
