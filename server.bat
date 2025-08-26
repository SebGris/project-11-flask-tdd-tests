@echo off
echo ========================================
echo   * Serving Flask app 'server'
echo ========================================
echo.
echo Starting server at http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.
echo Opening API interface in browser...
timeout /t 3 /nobreak > nul
start http://127.0.0.1:5000/
python -m flask --app server run
pause
