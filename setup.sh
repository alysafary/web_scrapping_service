#!/bin/bash

echo "🚀 Setting up Web Scraping Service..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found"

if ! command -v poetry &> /dev/null; then
    echo "📦 Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "✅ Poetry installed"
    echo "⚠️  You may need to restart your shell or run: source ~/.bashrc"
else
    echo "✅ Poetry found"
fi

echo "📦 Installing dependencies with Poetry..."
poetry install

echo "🎭 Installing Playwright browsers..."
poetry run playwright install chromium

if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Using default configuration."
    echo "💡 You can customize settings by editing the .env file."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the service:"
echo "  poetry run python main.py"
echo ""
echo "Or activate the virtual environment:"
echo "  poetry shell"
echo "  python main.py"
echo ""
echo "Visit http://localhost:8000/docs for API documentation"
echo ""
echo "To test the scraper:"
echo "  poetry run python test_scraper.py"
echo ""
