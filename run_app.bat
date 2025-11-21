@echo off
cd /d "%~dp0"

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Running Data Protection Simulator...
streamlit run data_protection_sim.py

pause
