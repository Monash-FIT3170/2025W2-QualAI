@echo off
title QualAI Project Launcher
color 0A

:start
echo.
echo  ========================================
echo  🚀 Welcome to QualAI Project Launcher 🚀
echo  ========================================
echo.

echo Checking prerequisites...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js 18+ first.
    pause
    exit /b 1
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!
echo.

echo Choose your startup option:
echo.
echo 1. 🚀 Start All Services (Recommended)
echo 2. 🐳 Start with Docker
echo 3. 🔧 Start Backend Only
echo 4. ⚛️  Start Frontend Only
echo 5. 🌐 Start Landing Page Only
echo 6. 📊 Check Service Status
echo 7. ❓ Show Help
echo 8. 🚪 Exit
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting all services...
    npm start
) else if "%choice%"=="2" (
    echo.
    echo 🐳 Starting with Docker...
    npm run dev:docker
) else if "%choice%"=="3" (
    echo.
    echo 🔧 Starting backend only...
    npm run dev:backend
) else if "%choice%"=="4" (
    echo.
    echo ⚛️ Starting frontend only...
    npm run dev:frontend
) else if "%choice%"=="5" (
    echo.
    echo 🌐 Starting landing page only...
    npm run dev:landing
) else if "%choice%"=="6" (
    echo.
    echo 📊 Checking service status...
    npm run status
    pause
    goto :start
) else if "%choice%"=="7" (
    echo.
    echo ❓ Showing help...
    npm run help
    pause
    goto :start
) else if "%choice%"=="8" (
    echo.
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice! Please try again.
    pause
    goto :start
)

echo.
echo 🎉 Services started successfully!
echo.
echo 🌐 Access your services at:
echo    Landing Page: http://localhost:3000
echo    Frontend:     http://localhost:5173
echo    Backend:      http://localhost:8000
echo.
echo Press any key to exit...
pause >nul
