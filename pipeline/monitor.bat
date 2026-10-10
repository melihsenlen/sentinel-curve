@echo off
setlocal
REM

SET SCRIPT_DIR=%~dp0

SET INTERVAL=1
SET DURATION=60
SET OUTPUT=%SCRIPT_DIR%..\data\data.csv

REM
:parse_args
IF "%~1"=="" GOTO end_parse
IF "%~1"=="--interval" (
    SET "INTERVAL=%~2"
    SHIFT
    SHIFT
    GOTO parse_args
)
IF "%~1"=="--duration" (
    SET "DURATION=%~2"
    SHIFT
    SHIFT
    GOTO parse_args
)
IF "%~1"=="--output" (
    SET "OUTPUT=%~2"
    SHIFT
    SHIFT
    GOTO parse_args
)
ECHO Unknown argument: %~1
EXIT /B 1
:end_parse

REM
IF NOT EXIST "%SCRIPT_DIR%..\monitor\build" (
    mkdir "%SCRIPT_DIR%..\monitor\build"
)

REM
where g++ >nul 2>&1
IF ERRORLEVEL 1 (
    ECHO g++ was not found on your PATH.
    EXIT /B 1
)

ECHO Building the monitor...
g++ -std=c++17 -I"%SCRIPT_DIR%..\monitor\include" "%SCRIPT_DIR%..\monitor\src\main.cpp" "%SCRIPT_DIR%..\monitor\src\monitor.cpp" -o "%SCRIPT_DIR%..\monitor\build\monitor.exe"
IF ERRORLEVEL 1 (
    ECHO Build failed.
    EXIT /B 1
)

REM
"%SCRIPT_DIR%..\monitor\build\monitor.exe" --interval %INTERVAL% --duration %DURATION% --output "%OUTPUT%"
IF ERRORLEVEL 1 (
    ECHO Monitor execution failed.
    EXIT /B 1
)