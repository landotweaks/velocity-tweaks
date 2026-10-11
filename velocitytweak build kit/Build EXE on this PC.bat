@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python is not installed. This local builder requires Python 3.10+.
  echo To build without installing Python on your PC, use the GitHub Actions steps in README.txt.
  pause
  exit /b 1
)
py -3 -m pip install --upgrade pyinstaller
if errorlevel 1 goto failed
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name VelocityPCOptimizer velocity_optimizer.py
if errorlevel 1 goto failed
echo.
echo Build complete: dist\VelocityPCOptimizer.exe
pause
exit /b 0
:failed
echo.
echo Build failed. Check the messages above.
pause
exit /b 1
