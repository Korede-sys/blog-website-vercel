@echo off
REM Blog Website Setup Script for Windows

echo 🚀 Setting up Blog Website...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install flask flask-sqlalchemy werkzeug

REM Create necessary directories
echo 📁 Creating directories...
if not exist static\uploads mkdir static\uploads
if not exist instance mkdir instance

REM Initialize database
echo 🗄️ Initializing database...
python -c "from app import app, db; app.app_context().push(); db.create_all()"

echo.
echo ✅ Setup complete!
echo.
echo 🌐 To start the website, run:
echo    venv\Scripts\activate
echo    python app.py
echo.
echo 📍 Then open your browser to:
echo    http://localhost:5000
echo.
echo 🔐 Admin login:
echo    URL: http://localhost:5000/admin/login
echo    Username: admin
echo    Password: admin123
echo.
pause
