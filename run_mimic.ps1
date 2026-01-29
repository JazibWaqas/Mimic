# MIMIC Quick Start Script
Write-Host "🚀 Starting MIMIC Backend..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\backend"
uvicorn main:app --reload --port 8000
