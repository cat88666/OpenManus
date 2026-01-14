#!/usr/bin/env python3
"""
Hugging Face Spaces自动部署脚本
使用方法: python scripts/deploy_hf.py
或: HF_TOKEN='xxx' python scripts/deploy_hf.py
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

class HFDeployer:
    """Hugging Face Spaces部署器"""
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.hf_username = "junk1107"
        self.hf_space_name = "ai-labor-platform"
        self.project_root = Path(__file__).parent.parent
        
    def validate(self):
        """验证部署前提条件"""
        print("🔍 验证部署前提条件...")
        
        if not self.hf_token:
            print("❌ 错误: 未设置HF_TOKEN环境变量")
            print("请运行: export HF_TOKEN='your_token_here'")
            return False
        
        if not (self.project_root / "platform" / "hf_spaces_app_mysql.py").exists():
            print("❌ 错误: 找不到应用文件")
            return False
        
        print("✅ 验证通过")
        return True
    
    def deploy(self):
        """执行部署"""
        print("🚀 开始部署到Hugging Face Spaces...\n")
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            repo_path = temp_path / "repo"
            
            try:
                # 克隆仓库
                print("📥 克隆HF Spaces仓库...")
                self._run_command([
                    "git", "clone",
                    f"https://huggingface.co/spaces/{self.hf_username}/{self.hf_space_name}",
                    str(repo_path)
                ], show_output=False)
                print("✅ 克隆成功\n")
                
                # 复制文件
                print("📋 复制应用文件...")
                self._copy_files(repo_path)
                print("✅ 文件复制成功\n")
                
                # 配置Git
                print("🔧 配置Git...")
                os.chdir(repo_path)
                self._run_command(["git", "config", "user.email", "dev@openmanus.com"], show_output=False)
                self._run_command(["git", "config", "user.name", "OpenManus Deployer"], show_output=False)
                print("✅ Git配置成功\n")
                
                # 检查更改
                result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
                if result.returncode == 0:
                    print("⚠️ 没有文件更改，跳过提交\n")
                else:
                    # 提交并推送
                    print("📤 提交并推送...")
                    self._run_command(["git", "add", "."], show_output=False)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self._run_command(
                        ["git", "commit", "-m", f"chore: 自动部署 - {timestamp}"],
                        show_output=False
                    )
                    
                    # 推送到HF
                    push_url = f"https://{self.hf_username}:{self.hf_token}@huggingface.co/spaces/{self.hf_username}/{self.hf_space_name}"
                    self._run_command(["git", "push", push_url, "main"], show_output=False)
                    print("✅ 推送成功\n")
                
                # 输出结果
                print("=" * 60)
                print("✅ 部署完成！")
                print("=" * 60)
                print(f"\n📍 应用地址: https://{self.hf_username}-{self.hf_space_name}.hf.space")
                print(f"📍 Space页面: https://huggingface.co/spaces/{self.hf_username}/{self.hf_space_name}")
                print("\n💡 提示:")
                print("- 应用将在1-2分钟内自动更新")
                print("- 您可以访问应用链接查看部署进度")
                print("- 如果出现问题，请查看Space的Logs页面")
                print("\n" + "=" * 60)
                
                return True
                
            except Exception as e:
                print(f"\n❌ 部署失败: {e}")
                return False
    
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
                print(f"  ✓ {src} → {dst}")
            else:
                print(f"  ⚠️ 警告: 找不到 {src}")
    
    def _run_command(self, cmd, show_output=True):
        """运行命令"""
        try:
            if show_output:
                result = subprocess.run(cmd, check=True)
            else:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            if not show_output:
                print(f"❌ 命令执行失败: {' '.join(cmd)}")
                if e.stderr:
                    print(f"错误: {e.stderr}")
            raise

def main():
    """主函数"""
    deployer = HFDeployer()
    
    if not deployer.validate():
        sys.exit(1)
    
    try:
        if deployer.deploy():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 部署被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 部署失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
