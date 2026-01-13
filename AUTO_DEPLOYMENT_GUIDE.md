# 自动部署流程指南

## 📋 目录

1. [部署流程概述](#部署流程概述)
2. [自动化部署脚本](#自动化部署脚本)
3. [GitHub Actions自动部署](#github-actions自动部署)
4. [手动快速部署](#手动快速部署)
5. [故障排除](#故障排除)
6. [部署检查清单](#部署检查清单)

---

## 部署流程概述

### 完整的部署流程

```
代码更新
  ↓
提交到GitHub
  ↓
触发GitHub Actions
  ↓
自动推送到HF Spaces
  ↓
HF Spaces自动构建
  ↓
应用自动部署
  ↓
应用在线运行
```

### 关键步骤

1. **代码更新** - 修改应用代码
2. **Git提交** - 提交到GitHub
3. **自动触发** - GitHub Actions自动运行
4. **推送到HF** - 自动推送到Hugging Face Spaces
5. **构建部署** - HF自动构建和部署
6. **上线运行** - 应用立即更新

---

## 自动化部署脚本

### 脚本1: 本地快速部署脚本

**文件**: `scripts/deploy_hf.sh`

```bash
#!/bin/bash

# AI数字员工平台 - Hugging Face Spaces快速部署脚本
# 使用方法: ./scripts/deploy_hf.sh

set -e

echo "🚀 开始部署到Hugging Face Spaces..."

# 配置
HF_TOKEN="${HF_TOKEN:-}"
HF_USERNAME="junk1107"
HF_SPACE_NAME="ai-labor-platform"
TEMP_DIR="/tmp/hf_deploy_$$"

# 检查Token
if [ -z "$HF_TOKEN" ]; then
    echo "❌ 错误: 未设置HF_TOKEN环境变量"
    echo "请运行: export HF_TOKEN='your_token_here'"
    exit 1
fi

# 创建临时目录
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo "📥 克隆HF Spaces仓库..."
git clone "https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME" repo
cd repo

echo "📋 复制应用文件..."
# 复制应用文件
cp "../../platform/hf_spaces_app_mysql.py" app.py
cp "../../platform/hf_spaces_requirements.txt" requirements.txt
cp "../../platform/Dockerfile_hf" Dockerfile
cp "../../platform/hf_spaces_readme.md" README.md

echo "🔧 配置Git..."
git config user.email "dev@openmanus.com"
git config user.name "OpenManus Deployer"

echo "📤 提交并推送..."
git add .
git commit -m "chore: 自动部署 - $(date '+%Y-%m-%d %H:%M:%S')"

# 使用Token进行身份验证
# 输入用户名和Token进行认证
git push

echo "✅ 部署完成！"
echo "📍 应用地址: https://$HF_USERNAME-$HF_SPACE_NAME.hf.space"
echo "📍 Space页面: https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME"

# 清理
cd /
rm -rf "$TEMP_DIR"

echo "💡 提示: 应用将在1-2分钟内自动更新"
```

### 脚本2: Python自动部署脚本

**文件**: `scripts/deploy_hf.py`

```python
#!/usr/bin/env python3
"""
Hugging Face Spaces自动部署脚本
使用方法: python scripts/deploy_hf.py
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

class HFDeployer:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.hf_username = "junk1107"
        self.hf_space_name = "ai-labor-platform"
        self.project_root = Path(__file__).parent.parent
        
    def validate(self):
        """验证部署前提条件"""
        if not self.hf_token:
            print("❌ 错误: 未设置HF_TOKEN环境变量")
            print("请运行: export HF_TOKEN='your_token_here'")
            return False
        
        if not (self.project_root / "platform" / "hf_spaces_app_mysql.py").exists():
            print("❌ 错误: 找不到应用文件")
            return False
        
        return True
    
    def deploy(self):
        """执行部署"""
        print("🚀 开始部署到Hugging Face Spaces...")
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            repo_path = temp_path / "repo"
            
            # 克隆仓库
            print("📥 克隆HF Spaces仓库...")
            self._run_command([
                "git", "clone",
                f"https://huggingface.co/spaces/{self.hf_username}/{self.hf_space_name}",
                str(repo_path)
            ])
            
            # 复制文件
            print("📋 复制应用文件...")
            self._copy_files(repo_path)
            
            # 配置Git
            print("🔧 配置Git...")
            os.chdir(repo_path)
            self._run_command(["git", "config", "user.email", "dev@openmanus.com"])
            self._run_command(["git", "config", "user.name", "OpenManus Deployer"])
            
            # 提交并推送
            print("📤 提交并推送...")
            self._run_command(["git", "add", "."])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._run_command(["git", "commit", "-m", f"chore: 自动部署 - {timestamp}"])
            
            # 推送到HF
            push_url = f"https://{self.hf_username}:{self.hf_token}@huggingface.co/spaces/{self.hf_username}/{self.hf_space_name}"
            self._run_command(["git", "push", push_url, "main"])
            
            print("✅ 部署完成！")
            print(f"📍 应用地址: https://{self.hf_username}-{self.hf_space_name}.hf.space")
            print(f"📍 Space页面: https://huggingface.co/spaces/{self.hf_username}/{self.hf_space_name}")
            print("💡 提示: 应用将在1-2分钟内自动更新")
    
    def _copy_files(self, repo_path):
        """复制应用文件"""
        files_to_copy = [
            ("platform/hf_spaces_app_mysql.py", "app.py"),
            ("platform/hf_spaces_requirements.txt", "requirements.txt"),
            ("platform/Dockerfile_hf", "Dockerfile"),
            ("platform/hf_spaces_readme.md", "README.md"),
        ]
        
        for src, dst in files_to_copy:
            src_path = self.project_root / src
            dst_path = repo_path / dst
            if src_path.exists():
                shutil.copy(src_path, dst_path)
            else:
                print(f"⚠️ 警告: 找不到 {src}")
    
    def _run_command(self, cmd):
        """运行命令"""
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败: {' '.join(cmd)}")
            print(f"错误: {e.stderr}")
            return False

def main():
    deployer = HFDeployer()
    
    if not deployer.validate():
        sys.exit(1)
    
    try:
        deployer.deploy()
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## GitHub Actions自动部署

### 配置GitHub Actions

**文件**: `.github/workflows/deploy-hf-spaces.yml`

```yaml
name: 自动部署到Hugging Face Spaces

on:
  push:
    branches:
      - main
    paths:
      - 'platform/hf_spaces_app_mysql.py'
      - 'platform/hf_spaces_requirements.txt'
      - 'platform/Dockerfile_hf'
      - 'platform/hf_spaces_readme.md'
      - '.github/workflows/deploy-hf-spaces.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: 检出代码
        uses: actions/checkout@v3
      
      - name: 设置Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: 安装依赖
        run: |
          pip install huggingface-hub
      
      - name: 部署到Hugging Face Spaces
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
          HF_USERNAME: junk1107
          HF_SPACE_NAME: ai-labor-platform
        run: |
          python scripts/deploy_hf.py
      
      - name: 部署成功通知
        if: success()
        run: |
          echo "✅ 应用已成功部署到Hugging Face Spaces"
          echo "📍 访问链接: https://junk1107-ai-labor-platform.hf.space"
      
      - name: 部署失败通知
        if: failure()
        run: |
          echo "❌ 部署失败，请检查日志"
          exit 1
```

### 配置GitHub Secrets

1. 访问 https://github.com/cat88666/OpenManus/settings/secrets/actions
2. 点击 **"New repository secret"**
3. 添加以下Secret:
   - **名称**: `HF_TOKEN`
   - **值**: `your_hf_token_here` (在GitHub Secrets中配置)

---

## 手动快速部署

### 方法1: 使用Shell脚本

```bash
# 1. 设置Token
export HF_TOKEN="your_hf_token_here"

# 2. 运行部署脚本
cd /home/ubuntu/OpenManus
bash scripts/deploy_hf.sh
```

### 方法2: 使用Python脚本

```bash
# 1. 设置Token
export HF_TOKEN="your_hf_token_here"

# 2. 运行部署脚本
cd /home/ubuntu/OpenManus
python scripts/deploy_hf.py
```

### 方法3: 手动部署（快速版）

```bash
# 1. 进入临时目录
cd /tmp
rm -rf hf_deploy
mkdir hf_deploy
cd hf_deploy

# 2. 克隆HF Spaces仓库
git clone https://huggingface.co/spaces/junk1107/ai-labor-platform repo
cd repo

# 3. 复制文件
cp /home/ubuntu/OpenManus/platform/hf_spaces_app_mysql.py app.py
cp /home/ubuntu/OpenManus/platform/hf_spaces_requirements.txt requirements.txt
cp /home/ubuntu/OpenManus/platform/Dockerfile_hf Dockerfile
cp /home/ubuntu/OpenManus/platform/hf_spaces_readme.md README.md

# 4. 配置Git
git config user.email "dev@openmanus.com"
git config user.name "OpenManus Deployer"

# 5. 提交并推送
git add .
git commit -m "chore: 自动部署 - $(date '+%Y-%m-%d %H:%M:%S')"
git push

# 6. 输入用户名和Token
# Username: junk1107
# Password: your_hf_token_here
```

---

## 故障排除

### 问题1: 部署失败 - Token无效

**症状**: 推送时提示认证失败

**解决方案**:
```bash
# 检查Token是否正确
echo $HF_TOKEN

# 重新设置Token
export HF_TOKEN="your_hf_token_here"

# 重试部署
python scripts/deploy_hf.py
```

### 问题2: 部署失败 - 文件不存在

**症状**: 复制文件时提示找不到文件

**解决方案**:
```bash
# 检查文件是否存在
ls -la /home/ubuntu/OpenManus/platform/hf_spaces_app_mysql.py

# 确保在项目根目录运行
cd /home/ubuntu/OpenManus
```

### 问题3: 部署失败 - Git配置错误

**症状**: 提交时提示Git配置错误

**解决方案**:
```bash
# 清除Git配置
git config --global --unset user.email
git config --global --unset user.name

# 重新配置
git config --global user.email "dev@openmanus.com"
git config --global user.name "OpenManus Deployer"
```

### 问题4: 应用部署后无法访问

**症状**: 推送成功但应用无法访问

**解决方案**:
1. 等待2-3分钟让HF构建和部署
2. 访问 https://huggingface.co/spaces/junk1107/ai-labor-platform 检查状态
3. 查看Logs页面查看错误信息
4. 如果仍然失败，检查Dockerfile配置

---

## 部署检查清单

### 部署前检查

- [ ] 代码已在本地测试
- [ ] 所有文件已保存
- [ ] Git已配置正确
- [ ] HF_TOKEN环境变量已设置
- [ ] 网络连接正常

### 部署中检查

- [ ] 脚本已启动
- [ ] 文件正在复制
- [ ] Git提交成功
- [ ] 推送到HF成功
- [ ] 没有错误消息

### 部署后检查

- [ ] HF Spaces显示"Running"状态
- [ ] 应用可以访问
- [ ] 所有功能正常
- [ ] 数据显示正确
- [ ] 没有错误日志

---

## 自动部署工作流

### 完整的更新和部署流程

```bash
# 1. 进入项目目录
cd /home/ubuntu/OpenManus

# 2. 更新代码
vim platform/hf_spaces_app_mysql.py  # 修改应用代码

# 3. 本地测试（可选）
streamlit run platform/hf_spaces_app_mysql.py

# 4. 提交到GitHub
git add .
git commit -m "feat: 添加新功能"
git push origin main

# 5. 自动部署（GitHub Actions自动运行）
# 或手动部署
export HF_TOKEN="your_hf_token_here"
python scripts/deploy_hf.py

# 6. 等待部署完成（1-2分钟）
# 7. 访问应用验证
# https://junk1107-ai-labor-platform.hf.space
```

---

## 部署时间估计

| 步骤 | 时间 |
|------|------|
| 克隆仓库 | 10-15秒 |
| 复制文件 | 5秒 |
| Git提交 | 5秒 |
| 推送到HF | 10-20秒 |
| HF构建 | 30-60秒 |
| HF部署 | 30-60秒 |
| 应用启动 | 10-30秒 |
| **总计** | **2-3分钟** |

---

## 监控部署状态

### 方法1: 查看Space页面

访问 https://huggingface.co/spaces/junk1107/ai-labor-platform

查看状态指示器:
- 🟢 Running - 应用正常运行
- 🟡 Starting - 应用正在启动
- 🔴 Error - 应用出错

### 方法2: 查看Logs

1. 进入Space页面
2. 点击 **"Logs"** 标签
3. 查看应用日志

### 方法3: 访问应用

直接访问 https://junk1107-ai-labor-platform.hf.space

如果能正常加载，说明部署成功

---

## 常见问题

### Q: 部署需要多长时间？
A: 通常2-3分钟。如果超过5分钟，请检查Logs页面。

### Q: 部署失败后会怎样？
A: 应用保持之前的版本运行，不会中断服务。

### Q: 可以回滚到之前的版本吗？
A: 可以。在Git历史中找到之前的提交，重新推送即可。

### Q: 部署时应用会中断吗？
A: 不会。HF会先构建新版本，然后切换。

### Q: 如何禁用自动部署？
A: 删除 `.github/workflows/deploy-hf-spaces.yml` 文件。

---

## 最佳实践

1. **本地测试** - 部署前在本地测试代码
2. **清晰的提交信息** - 使用有意义的commit message
3. **小步骤提交** - 避免一次性提交大量更改
4. **监控部署** - 部署后检查应用状态
5. **保持备份** - 重要更改前备份代码

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `scripts/deploy_hf.sh` | Shell部署脚本 |
| `scripts/deploy_hf.py` | Python部署脚本 |
| `.github/workflows/deploy-hf-spaces.yml` | GitHub Actions工作流 |
| `platform/hf_spaces_app_mysql.py` | Streamlit应用 |
| `platform/hf_spaces_requirements.txt` | Python依赖 |
| `platform/Dockerfile_hf` | Docker配置 |

---

## 快速参考

### 快速部署命令

```bash
# 设置Token
export HF_TOKEN="your_hf_token_here"

# 快速部署
cd /home/ubuntu/OpenManus && python scripts/deploy_hf.py
```

### 查看部署状态

```bash
# 访问Space页面
open https://huggingface.co/spaces/junk1107/ai-labor-platform

# 访问应用
open https://junk1107-ai-labor-platform.hf.space
```

---

**最后更新**: 2026-01-13  
**版本**: v1.0

---

祝您部署顺利！🚀
