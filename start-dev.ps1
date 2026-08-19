# DevLens Development Startup Script
# Starts infrastructure via Docker Compose, then backend and frontend locally.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DevLens Dev Environment Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Start infrastructure containers
Write-Host "`n[1/3] Starting infrastructure containers (postgres, redis, qdrant)..." -ForegroundColor Yellow
docker compose up -d postgres redis qdrant
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start Docker containers. Make sure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for containers to be healthy..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 2. Start backend
Write-Host "`n[2/3] Starting backend (FastAPI on http://localhost:8000)..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendPath'; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

Start-Sleep -Seconds 3

# 3. Start frontend
Write-Host "`n[3/3] Starting frontend (Next.js on http://localhost:3000)..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; npm run dev" -WindowStyle Normal

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  DevLens is starting up!" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:8000/api/v1/docs" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
