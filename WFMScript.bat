@echo off
setlocal
chcp 65001 >nul

set "PATH=C:\Users\%USERNAME%\AppData\Local\Python\bin;C:\Users\%USERNAME%\AppData\Local\Python\pythoncore-3.14-64\Scripts;%PATH%"

cd /d "%~dp0"

"C:\Users\%USERNAME%\AppData\Local\Python\bin\python.exe" mercato.py

pause