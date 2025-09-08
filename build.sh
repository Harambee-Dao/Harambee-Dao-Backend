#!/bin/bash
set -e

echo "🔧 Starting Harambee DAO Backend Build..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Install package in development mode
echo "📦 Installing package..."
pip install -e .

echo "✅ Build completed successfully!"
