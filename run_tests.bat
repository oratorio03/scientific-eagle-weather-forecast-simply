@echo off
python -m pytest tests\ -v
if errorlevel 1 (
    echo Tests FAILED
    exit /b 1
) else (
    echo Tests PASSED
)
