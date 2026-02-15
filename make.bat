@echo off
echo ==========================================
echo Starting build process for Vorgify...
echo ==========================================
echo.

rem --- STEP 1: EXTRACT VERSION FROM PYTHON FILE ---
echo Extracting version number from vorgify_app.py...

rem Simplified Regex to avoid Batch special characters like pipe (|)
for /f "delims=" %%i in ('python -c "import re; print(re.search(r'__version__\s*=\s*[\x22\x27](.+?)[\x22\x27]', open('vorgify_app.py').read()).group(1))"') do set APP_VERSION=%%i

echo Found Version: %APP_VERSION%
echo.

rem --- STEP 2: CLEANUP ---
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo Creating EXE file for Version %APP_VERSION%...
echo This might take a moment. Please wait.
echo.

rem --- STEP 3: BUILD WITH PYINSTALLER ---
rem Ensure --name uses the variable correctly
python -m PyInstaller --noconsole --onefile --copy-metadata=imageio --copy-metadata=moviepy --icon=vorgify_logo.ico --add-data "vorgify_logo.png;." --name "vorgify_v%APP_VERSION%" vorgify_app.py

echo.
echo ==========================================
if exist "dist\vorgify_v%APP_VERSION%.exe" (
    echo Build successful!
    echo Created: dist\Vorgify_v%APP_VERSION%.exe
) else (
    echo ERROR during build! Please check the output logs above.
)
echo ==========================================
echo.

pause