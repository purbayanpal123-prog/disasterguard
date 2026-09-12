@echo off
title DISASTERGUARD COMMAND ENGINE - PURBAYAN PAL
cd /d "C:\Users\PURBAYAN PAL\.gemini\antigravity\scratch\disasterguard"
echo ==============================================================================
echo DISASTERGUARD: AUTONOMOUS BASIN TELEMETRY ENGINE
echo Copyright (c) 2026 Purbayan Pal. All Rights Reserved.
echo Architected & Engineered by: Purbayan Pal
echo ==============================================================================
echo.
echo [*] Starting Python Telemetry Server on Port 8080...
start /b "" ".\venv\Scripts\python.exe" server.py
timeout /t 3 /nobreak >nul

echo [*] Starting Cloudflare HTTPS Tunnel for Mobile Phones...
start /b "" ".\cloudflared.exe" tunnel --url http://localhost:8080
timeout /t 4 /nobreak >nul

echo [*] Launching Admin Command Center in Browser...
start "" "http://localhost:8080"

echo.
echo ==============================================================================
echo [ONLINE] DISASTERGUARD IS FULLY OPERATIONAL!
echo - Laptop Admin: http://localhost:8080
echo ==============================================================================
pause
