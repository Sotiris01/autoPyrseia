@echo off
echo ================================================
echo   autoPyrseia v2.0 - Executable Builder
echo   Modular Architecture Build Process
echo ================================================
echo.
echo Checking PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller not found!
    echo Please install PyInstaller: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo Building autoPyrseia executable...
echo.
echo This may take a few minutes...
echo.

pyinstaller autopyrseia.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for errors.
) else (
    echo.
    echo SUCCESS: autoPyrseia executable created!
    echo.
    echo Output location: dist\autoPyrseia\
    echo.
    echo You can now run the executable without Python installed.
)

echo.
pause