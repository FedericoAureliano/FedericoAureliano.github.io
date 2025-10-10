#!/bin/bash

echo "Setting up development environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "Error: Pandoc is not installed."
    echo "Please install Pandoc from https://pandoc.org/installing.html"
    echo "On macOS, you can use: brew install pandoc"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To build the website, run:"
echo "  ./build.sh"
