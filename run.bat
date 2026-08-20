@echo off
cd /d "%~dp0"
set "PYTHONPATH="
".venv\Scripts\python.exe" -m streamlit run app.py
pause