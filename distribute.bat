@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   MySkill - 技能分发脚本
echo ============================================
echo.

set /p TARGET="请输入目标路径 (如 C:\Users\Gove2\.claude): "

:: 去掉末尾的引号和反斜杠
set TARGET=%TARGET:"=%
if "%TARGET:~-1%"=="\" set TARGET=%TARGET:~0,-1%

set SKILLS_DIR=%TARGET%\skills

if not exist "%TARGET%" (
    echo [错误] 路径不存在: %TARGET%
    pause
    exit /b 1
)

if not exist "%SKILLS_DIR%" (
    mkdir "%SKILLS_DIR%"
    echo [创建] 技能目录: %SKILLS_DIR%
)

echo.
echo 即将同步以下技能到 %SKILLS_DIR%:
echo   - send-email-skill
echo   - kb
echo   - godot-procedural-kit
echo   - make-tutorial
echo   - pdf-to-markdown
echo.

set SKILLS=send-email-skill kb godot-procedural-kit make-tutorial pdf-to-markdown

for %%s in (%SKILLS%) do (
    set SRC=%~dp0%%s
    set DST=%SKILLS_DIR%\%%s

    if exist "!DST!" (
        echo [检测] %%s 已存在
        set /p CONFIRM="   覆盖? (y/n): "
        if /i "!CONFIRM!"=="y" (
            rmdir /s /q "!DST!"
            xcopy /e /i /q "!SRC!" "!DST!"
            echo    [完成] %%s 已覆盖
        ) else (
            echo    [跳过] %%s
        )
    ) else (
        xcopy /e /i /q "!SRC!" "!DST!"
        echo [新增] %%s
    )
)

echo.
echo ============================================
echo   同步完成
echo ============================================
pause