#!/bin/bash
# Build script for Vercel deployment
# This installs Playwright browsers and dependencies

echo "Installing Playwright browsers..."
python -m playwright install chromium
python -m playwright install-deps chromium

