@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   MySkill - Skill Distribute
echo ============================================
echo.

set /p TARGET="Target path, e.g. C:\Users\Gove2\.claude: "

set TARGET=%TARGET:"=%
if "%TARGET:~-1%"=="\" set TARGET=%TARGET:~0,-1%

set SKILLS_DIR=%TARGET%\skills

if not exist "%TARGET%" (
    echo [ERROR] Path not found: %TARGET%
    pause
    exit /b 1
)

if not exist "%SKILLS_DIR%" (
    mkdir "%SKILLS_DIR%"
    echo [CREATE] %SKILLS_DIR%
)

set SCRIPT_DIR=%~dp0

echo.
echo Skills found:
for /d %%d in ("%SCRIPT_DIR%*") do (
    if exist "%%d\SKILL.md" (
        echo   - %%~nxd
    )
)
echo.

for /d %%d in ("%SCRIPT_DIR%*") do (
    if exist "%%d\SKILL.md" (
        call :sync "%%~nxd"
    )
)

echo.
echo ============================================
echo   Done.
echo ============================================
pause
exit /b 0

:sync
set SRC=%SCRIPT_DIR%%~1
set DST=%SKILLS_DIR%\%~1

if not exist "%DST%" goto :sync_copy

echo [CHECK] %~1 exists
set /p CONFIRM="   Overwrite? y/n: "
if /i "%CONFIRM%"=="y" goto :sync_overwrite
echo    [SKIP] %~1
goto :eof

:sync_overwrite
rmdir /s /q "%DST%"
xcopy /e /i /q "%SRC%" "%DST%"
echo    [OK] %~1 overwritten
goto :eof

:sync_copy
xcopy /e /i /q "%SRC%" "%DST%"
echo [NEW] %~1
goto :eof