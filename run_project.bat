@echo off
title MediPredict Full Stack

start "Backend" cmd /k "cd /d C:\Users\ASA\Desktop\Team 8\CNPM\App\backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

start "Frontend" cmd /k "cd /d C:\Users\ASA\Desktop\Team 8\CNPM\App\frontend && pnpm run dev"