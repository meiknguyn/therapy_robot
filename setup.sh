#!/bin/bash
# Setup script for Therapy Robot project

set -e

echo "Setting up Therapy Robot environment..."

# Check for Python development headers
echo "Checking for Python development headers..."
if ! python3 -c "import sysconfig; sysconfig.get_path('include')" 2>/dev/null; then
    echo "WARNING: Python development headers may be missing."
    echo "If spidev installation fails, install them with:"
    echo "  sudo apt install python3-dev"
    echo ""
fi

# Check if virtual environment already exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run the therapy robot:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Set your API key: export GEMINI_API_KEY='YOUR_KEY_HERE'"
echo "  3. Run: python -m therapy_robot.main"
echo ""

