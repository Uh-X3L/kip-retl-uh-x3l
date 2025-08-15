#!/bin/bash
set -e

echo "🚀 Setting up AI Agent System for Issue #70"

# Check prerequisites
echo "🔍 Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required"; exit 1; }

echo "✅ Prerequisites check passed"

# Setup Python environment
echo "🐍 Setting up Python environment..."
cd src/backend
pip install -r requirements.txt
cd ../..

echo "✅ Setup completed successfully!"
