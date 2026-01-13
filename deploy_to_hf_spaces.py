#!/usr/bin/env python3
"""
Hugging Face Spaces 自动部署脚本
用于自动创建和部署应用到Hugging Face Spaces
"""

import os
import subprocess
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo
from huggingface_hub.utils import RepositoryNotFoundError

def deploy_to_hf_spaces(token, space_name="ai-labor-platform", private=False):
    """
    部署应用到Hugging Face Spaces
    
    Args:
        token: Hugging Face API Token
        space_name: Space名称
        private: 是否为私有Space
    """
    
    print("🚀 开始部署到Hugging Face Spaces...")
    
    # 初始化API
    api = HfApi(token=token)
    
    # 获取用户信息
    try:
        user_info = api.whoami()
        username = user_info["name"]
        print(f"✅ 已认证用户: {username}")
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        return False
    
    # 创建Space仓库
    space_repo_id = f"{username}/{space_name}"
    
    try:
        print(f"📦 创建Space: {space_repo_id}")
        create_repo(
            repo_id=space_repo_id,
            repo_type="space",
            space_sdk="docker",
            private=private,
            exist_ok=True,
            token=token
        )
        print(f"✅ Space创建成功")
    except Exception as e:
        print(f"❌ Space创建失败: {e}")
        return False
    
    # 克隆Space仓库
    space_dir = f"/tmp/{space_name}"
    
    if os.path.exists(space_dir):
        print(f"📂 清空旧目录: {space_dir}")
        subprocess.run(["rm", "-rf", space_dir], check=True)
    
    print(f"📥 克隆Space仓库...")
    clone_url = f"https://huggingface.co/spaces/{space_repo_id}"
    
    try:
        subprocess.run(
            ["git", "clone", clone_url, space_dir],
            check=True,
            capture_output=True
        )
        print(f"✅ 仓库克隆成功")
    except Exception as e:
        print(f"❌ 仓库克隆失败: {e}")
        return False
    
    # 复制应用文件
    print(f"📋 复制应用文件...")
    
    try:
        # 复制主应用文件
        subprocess.run(
            ["cp", "platform/hf_spaces_app_mysql.py", f"{space_dir}/app.py"],
            check=True
        )
        
        # 复制requirements.txt
        requirements_content = """streamlit==1.28.0
pandas==2.0.0
plotly==5.17.0
requests==2.31.0
mysql-connector-python==8.2.0
"""
        with open(f"{space_dir}/requirements.txt", "w") as f:
            f.write(requirements_content)
        
        # 创建README
        readme_content = """# AI数字员工平台

这是OpenManus AI数字员工平台在Hugging Face Spaces上的部署版本。

## 功能特性

- 📊 实时仪表板
- 🎯 机会管理
- 📁 项目管理
- 📚 知识库
- 📈 数据分析
- 🔧 系统管理

## 技术栈

- Streamlit
- MySQL
- Plotly

## 快速开始

1. 访问应用
2. 浏览各个功能模块
3. 创建数据并分析

## 环境变量

配置以下环境变量以连接到您的MySQL数据库：

- `DB_HOST`: 数据库主机
- `DB_PORT`: 数据库端口
- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `DB_NAME`: 数据库名称

## 项目信息

- 版本: v1.0
- GitHub: https://github.com/cat88666/OpenManus
"""
        with open(f"{space_dir}/README.md", "w") as f:
            f.write(readme_content)
        
        print(f"✅ 文件复制成功")
    except Exception as e:
        print(f"❌ 文件复制失败: {e}")
        return False
    
    # 配置Git
    print(f"🔧 配置Git...")
    
    try:
        subprocess.run(
            ["git", "config", "user.email", "dev@openmanus.com"],
            cwd=space_dir,
            check=True
        )
        subprocess.run(
            ["git", "config", "user.name", "OpenManus Deployer"],
            cwd=space_dir,
            check=True
        )
        print(f"✅ Git配置成功")
    except Exception as e:
        print(f"❌ Git配置失败: {e}")
        return False
    
    # 提交并推送
    print(f"📤 提交并推送代码...")
    
    try:
        subprocess.run(
            ["git", "add", "."],
            cwd=space_dir,
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Deploy AI Labor Platform to Hugging Face Spaces"],
            cwd=space_dir,
            check=True
        )
        subprocess.run(
            ["git", "push"],
            cwd=space_dir,
            check=True
        )
        print(f"✅ 代码推送成功")
    except Exception as e:
        print(f"❌ 代码推送失败: {e}")
        return False
    
    # 输出结果
    print("\n" + "="*60)
    print("🎉 部署完成！")
    print("="*60)
    print(f"\n📍 应用地址: https://{username}-{space_name}.hf.space")
    print(f"📍 Space页面: https://huggingface.co/spaces/{space_repo_id}")
    print("\n✨ 您的应用现在已在线运行！")
    print("\n💡 提示:")
    print("- 首次加载可能需要1-2分钟")
    print("- 在Space设置中添加环境变量以连接MySQL数据库")
    print("- 环境变量:")
    print("  - DB_HOST")
    print("  - DB_PORT")
    print("  - DB_USER")
    print("  - DB_PASSWORD")
    print("  - DB_NAME")
    print("\n" + "="*60)
    
    return True

def main():
    """主函数"""
    
    # 获取Token
    token = os.getenv("HF_TOKEN")
    
    if not token:
        print("❌ 错误: 未找到HF_TOKEN环境变量")
        print("请设置: export HF_TOKEN='your_token_here'")
        sys.exit(1)
    
    # 部署
    success = deploy_to_hf_spaces(token)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
