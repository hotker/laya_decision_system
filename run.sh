#!/bin/bash
# Laya AI Decision System - Startup Script

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Display welcome message
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🧠 Laya AI Decision System                           ║"
echo "║        Laya AI Decision System v2.0.0                      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "🐍 Python version: $python_version"
echo ""

# Check Laya service
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Laya AI service is running"
else
    echo "⚠️  Laya AI service is not running"
    echo "   Start command: cd /Users/hotker/Workspace/laya && ./start-laya.sh"
    echo ""
fi

# Execute main program
exec python3 src/main.py "$@"