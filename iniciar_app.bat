@echo off
title Estampador de Logos ARCA
cd /d "%~dp0"
cls

echo =======================================================
echo    Estampador de Logos para Facturas ARCA / AFIP
echo =======================================================
echo.
echo Abriendo la aplicacion en su navegador web...
echo.

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -m streamlit run app.py
    goto FIN
)

set "UV_EXE=%USERPROFILE%\.local\bin\uv.exe"
if exist "%UV_EXE%" (
    "%UV_EXE%" run streamlit run app.py
    goto FIN
)

uv run streamlit run app.py

:FIN
pause
