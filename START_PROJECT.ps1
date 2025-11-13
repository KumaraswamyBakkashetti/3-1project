# ============================================================================
# AgentMonitor Startup Script
# ============================================================================
# This script starts both backend and frontend servers

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "AgentMonitor - Dual-LLM Code Generation System" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up environment..." -ForegroundColor Yellow

# Check for API key in environment (do not hardcode keys here)
if ($env:GEMINI_API_KEY) {
    Write-Host "✓ agent API key found (value hidden)" -ForegroundColor Green
} else {
    Write-Host "⚠️ agent API key not set. Please set GEMINI_API_KEY in your environment before starting the backend." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Yellow
Write-Host ""

# Start Backend (Python FastAPI)
Write-Host "Starting Backend Server (port 8080)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PSScriptRoot\backend' ; python app.py" `
    -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Frontend (React)
Write-Host "Starting Frontend Server (port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PSScriptRoot\frontend' ; npm start" `
    -WindowStyle Normal

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "Servers Starting!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8080" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wait 10-15 seconds for servers to fully start..." -ForegroundColor Yellow
Write-Host "Then open http://localhost:3000 in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
