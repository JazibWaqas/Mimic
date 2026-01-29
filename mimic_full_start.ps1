# MIMIC Full Stack Automator
Write-Host "🔥 Fire up the Engines! Starting MIMIC Backend and Frontend..." -ForegroundColor Yellow

# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '--- MIMIC BACKEND ---' -ForegroundColor Cyan; cd backend; uvicorn main:app --reload --port 8000"

# Start Frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '--- MIMIC FRONTEND ---' -ForegroundColor Green; cd frontend; npm run dev"

Write-Host "✅ Both servers are launching in new windows. Happy editing!" -ForegroundColor Green
