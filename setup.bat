@echo off
REM JAGAPADI v2.2 - Windows Installation Script
REM install.bat

echo ========================================
echo JAGAPADI v2.2 - Windows Installer
echo ========================================

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found, checking version...
python -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)"
if %errorlevel% neq 0 (
    echo ERROR: Python 3.8+ required
    echo Please upgrade Python
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Creating directories...
python install.py --skip-tests

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start JAGAPADI:
echo 1. Activate environment: venv\Scripts\activate.bat
echo 2. Start server: python server.py
echo 3. Start client: python client_2.py
echo.
pause

---

#!/bin/bash
# JAGAPADI v2.2 - Linux/macOS Installation Script
# install.sh

set -e  # Exit on any error

echo "========================================"
echo "JAGAPADI v2.2 - Linux/macOS Installer"
echo "========================================"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager"
    exit 1
fi

echo "Python found, checking version..."
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" || {
    echo "ERROR: Python 3.8+ required"
    echo "Please upgrade Python"
    exit 1
}

# Install system dependencies (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux, checking system dependencies..."
    
    if command -v apt &> /dev/null; then
        echo "Installing system dependencies (Ubuntu/Debian)..."
        sudo apt update
        sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libfontconfig1 libxrender1
    elif command -v yum &> /dev/null; then
        echo "Installing system dependencies (CentOS/RHEL)..."
        sudo yum install -y mesa-libGL glib2 libSM libXext fontconfig libXrender
    else
        echo "Please install system dependencies manually:"
        echo "  - OpenGL libraries"
        echo "  - GLib2"
        echo "  - X11 libraries"
    fi
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
python -m pip install -r jagapadi_requirements.txt

echo "Creating directories..."
python install.py --skip-tests

echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "To start JAGAPADI:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Start server: python server.py"
echo "3. Start client: python client_2.py"
echo ""

# Make scripts executable
chmod +x server.py client_2.py
