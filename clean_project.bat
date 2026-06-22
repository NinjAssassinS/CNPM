@echo off
chcp 65001 >nul
title Dọn dẹp project - Xóa thư viện & cache

echo ============================================
echo  CLEAN PROJECT - XOA THU VIEN VA CACHE
echo ============================================
echo.
echo Project se giam nhe dung luong.
echo De chay lai, can cai dat lai thu vien:
echo   - Frontend: pnpm install
echo   - Backend:  pip install -r requirements.txt
echo.
echo ============================================
echo.

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%App\frontend"
set "BACKEND=%ROOT%App\backend"

REM -------------------------------------------------
echo [1/6] Xoa node_modules (Frontend)...
if exist "%FRONTEND%\node_modules" (
    rd /s /q "%FRONTEND%\node_modules"
    echo   OK - Da xoa node_modules
) else (
    echo   Khong tim thay node_modules
)

REM -------------------------------------------------
echo [2/6] Xoa dist (Frontend - build output)...
if exist "%FRONTEND%\dist" (
    rd /s /q "%FRONTEND%\dist"
    echo   OK - Da xoa dist
) else (
    echo   Khong tim thay dist
)

REM -------------------------------------------------
echo [3/6] Xoa .mgx cache...
if exist "%FRONTEND%\.mgx" (
    rd /s /q "%FRONTEND%\.mgx"
    echo   OK - Da xoa .mgx (frontend)
) else (
    echo   Khong tim thay .mgx (frontend)
)
if exist "%ROOT%App\.mgx" (
    rd /s /q "%ROOT%App\.mgx"
    echo   OK - Da xoa .mgx (App)
) else (
    echo   Khong tim thay .mgx (App)
)

REM -------------------------------------------------
echo [4/6] Xoa __pycache__ (Python bytecode)...
for /d /r "%BACKEND%" %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d"
        echo   OK - Da xoa: %%d
    )
)

REM -------------------------------------------------
echo [5/6] Xoa file log...
if exist "%BACKEND%\logs" (
    rd /s /q "%BACKEND%\logs"
    echo   OK - Da xoa logs
) else (
    echo   Khong tim thay logs
)
if exist "%BACKEND%\startup_test.log" del /q "%BACKEND%\startup_test.log"
if exist "%BACKEND%\startup_test_err.log" del /q "%BACKEND%\startup_test_err.log"

REM -------------------------------------------------
echo [6/6] Xoa prerender (Frontend)...
if exist "%FRONTEND%\prerender" (
    rd /s /q "%FRONTEND%\prerender"
    echo   OK - Da xoa prerender
) else (
    echo   Khong tim thay prerender
)

REM -------------------------------------------------
echo.
echo ============================================
echo  HOAN TAT! Project da duoc don dep.
echo ============================================
echo.
echo Con lai: %ROOT%
dir "%ROOT%" /a /b
echo.
echo ============================================
echo  De chay lai du an, thuc hien:
echo   1. Frontend: pnpm install
echo   2. Backend:  pip install -r App\backend\requirements.txt
echo   3. Chay:     run_project.bat
echo ============================================
pause
