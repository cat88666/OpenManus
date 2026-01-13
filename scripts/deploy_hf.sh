#!/bin/bash

# AI数字员工平台 - Hugging Face Spaces快速部署脚本
# 使用方法: ./scripts/deploy_hf.sh
# 或: bash scripts/deploy_hf.sh

set -e

echo "🚀 开始部署到Hugging Face Spaces..."

# 配置
HF_TOKEN="${HF_TOKEN:-}"
HF_USERNAME="junk1107"
HF_SPACE_NAME="ai-labor-platform"
TEMP_DIR="/tmp/hf_deploy_$$"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 检查Token
if [ -z "$HF_TOKEN" ]; then
    echo "❌ 错误: 未设置HF_TOKEN环境变量"
    echo "请运行: export HF_TOKEN='your_token_here'"
    exit 1
fi

# 检查必要的文件
if [ ! -f "$PROJECT_ROOT/platform/hf_spaces_app_mysql.py" ]; then
    echo "❌ 错误: 找不到应用文件"
    exit 1
fi

# 创建临时目录
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo "📥 克隆HF Spaces仓库..."
git clone "https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME" repo 2>/dev/null || {
    echo "❌ 克隆失败，请检查Token和Space名称"
    exit 1
}
cd repo

echo "📋 复制应用文件..."
# 复制应用文件
cp "$PROJECT_ROOT/platform/hf_spaces_app_mysql.py" app.py
cp "$PROJECT_ROOT/platform/hf_spaces_requirements.txt" requirements.txt
cp "$PROJECT_ROOT/platform/Dockerfile_hf" Dockerfile
cp "$PROJECT_ROOT/platform/hf_spaces_readme.md" README.md

echo "🔧 配置Git..."
git config user.email "dev@openmanus.com"
git config user.name "OpenManus Deployer"

echo "📤 提交并推送..."
git add .

# 检查是否有更改
if git diff --cached --quiet; then
    echo "⚠️ 没有文件更改，跳过提交"
else
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "chore: 自动部署 - $TIMESTAMP"
    
    # 使用Token进行身份验证
    git push "https://$HF_USERNAME:$HF_TOKEN@huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME" main 2>&1 | grep -v "^remote:" || true
fi

echo ""
echo "✅ 部署完成！"
echo "📍 应用地址: https://$HF_USERNAME-$HF_SPACE_NAME.hf.space"
echo "📍 Space页面: https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME"
echo ""
echo "💡 提示: 应用将在1-2分钟内自动更新"
echo "⏱️ 您可以访问应用链接查看部署进度"

# 清理
cd /
rm -rf "$TEMP_DIR"

exit 0
