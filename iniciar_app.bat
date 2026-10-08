@echo off
title Estampador de Logos ARCA
cls

echo =======================================================
echo    Estampador de Logos para Facturas ARCA / AFIP
echo =======================================================
echo.
echo Abriendo la aplicacion en su navegador web...
echo.

set "UV_EXE=%USERPROFILE%\.local\bin\uv.exe"

if exist "%UV_EXE%" (
    "%UV_EXE%" run streamlit run app.py
    goto FIN
)

uv run streamlit run app.py

:FIN
pause
