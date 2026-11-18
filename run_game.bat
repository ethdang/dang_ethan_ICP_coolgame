:: used gpt 5.6 luna

:: prompt:
:: is there a more efficient way to setup the server and 
:: run main using a single command?
:: .\run_game.bat

@echo off
cd /d "%~dp0"

taskkill /FI "WINDOWTITLE eq Game Server*" /T /F >nul 2>&1
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python(\\.exe)?$' -and $_.CommandLine -like '*server.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

start "Game Server" cmd /k python server.py
timeout /t 1 /nobreak >nul

start "Player 1" cmd /k python main.py
start "Player 2" cmd /k python main.py