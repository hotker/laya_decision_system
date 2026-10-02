#!/bin/bash
# Laya AI 决策系统 - 启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 显示欢迎信息
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🧠 Laya AI 决策系统                                   ║"
echo "║        Laya AI Decision System v1.0.0                      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python 版本
python_version=$(python3 --version 2>&1)
echo "🐍 Python 版本：$python_version"
echo ""

# 检查 Laya 服务
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Laya AI 服务已运行"
else
    echo "⚠️  Laya AI 服务未运行"
    echo "   启动命令：cd /Users/hotker/Workspace/laya && ./start-laya.sh"
    echo ""
fi

# 执行主程序
exec python3 src/main.py "$@"