@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 velocity_optimizer.py
) else (
  python velocity_optimizer.py
)
if errorlevel 1 (
  echo.
  echo If Python is not installed, install Python 3 from python.org and enable "Add Python to PATH".
  pause
)
