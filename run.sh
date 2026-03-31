#!/bin/bash

echo "🚀 启动回译训练系统..."

# 进入项目目录（可选，如果你已经在目录内可以删掉）
cd "$(dirname "$0")"

# 激活虚拟环境（如果有）
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 拉取最新数据
echo "📥 正在同步最新数据..."
git pull

# 启动 Streamlit
echo "🌐 启动 Web 界面..."
streamlit run app.py

# 关闭后自动提交（可选）
echo "📤 正在提交数据..."
git add translation_train.db
git commit -m "auto update $(date '+%Y-%m-%d %H:%M:%S')" || echo "无变化"
git push

echo "✅ 完成"