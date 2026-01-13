# 部署快速参考卡

## 🚀 快速部署命令

### 方法1: Python脚本（推荐）

```bash
export HF_TOKEN="your_hf_token_here"
cd /home/ubuntu/OpenManus
python scripts/deploy_hf.py
```

### 方法2: Shell脚本

```bash
export HF_TOKEN="your_hf_token_here"
cd /home/ubuntu/OpenManus
bash scripts/deploy_hf.sh
```

### 方法3: 自动部署（GitHub Actions）

只需推送代码到GitHub main分支，GitHub Actions会自动部署：

```bash
cd /home/ubuntu/OpenManus
git add .
git commit -m "feat: 新功能"
git push origin main
```

---

## 📋 完整的更新和部署流程

```bash
# 1. 进入项目目录
cd /home/ubuntu/OpenManus

# 2. 更新代码
vim platform/hf_spaces_app_mysql.py

# 3. 本地测试（可选）
streamlit run platform/hf_spaces_app_mysql.py

# 4. 提交到GitHub
git add .
git commit -m "feat: 添加新功能"
git push origin main

# 5. 等待自动部署（GitHub Actions）
# 或手动部署
export HF_TOKEN="your_hf_token_here"
python scripts/deploy_hf.py

# 6. 等待1-2分钟让HF构建和部署
# 7. 访问应用验证
# https://junk1107-ai-labor-platform.hf.space
```

---

## ⏱️ 部署时间

| 步骤 | 时间 |
|------|------|
| 脚本执行 | 1-2分钟 |
| HF构建 | 30-60秒 |
| HF部署 | 30-60秒 |
| 应用启动 | 10-30秒 |
| **总计** | **2-3分钟** |

---

## 🔗 重要链接

| 链接 | 说明 |
|------|------|
| https://junk1107-ai-labor-platform.hf.space | 应用地址 |
| https://huggingface.co/spaces/junk1107/ai-labor-platform | Space管理页面 |
| https://github.com/cat88666/OpenManus | GitHub仓库 |
| https://github.com/cat88666/OpenManus/settings/secrets/actions | GitHub Secrets |

---

## 🔐 关键信息

| 项目 | 值 |
|------|-----|
| **HF用户名** | junk1107 |
| **Space名称** | ai-labor-platform |
| **HF Token** | 已在GitHub Secrets中配置 |
| **GitHub仓库** | cat88666/OpenManus |

---

## ✅ 部署检查清单

部署前：
- [ ] 代码已测试
- [ ] HF_TOKEN已设置
- [ ] 网络连接正常

部署后：
- [ ] HF Space显示"Running"
- [ ] 应用可访问
- [ ] 功能正常
- [ ] 无错误日志

---

## 🆘 快速故障排除

### 部署失败

```bash
# 检查Token
echo $HF_TOKEN

# 重新设置Token
export HF_TOKEN="your_hf_token_here"

# 重试
python scripts/deploy_hf.py
```

### 应用无法访问

1. 等待2-3分钟
2. 访问Space页面检查状态
3. 查看Logs页面查看错误
4. 如果仍然失败，手动重启

### 查看应用日志

访问: https://huggingface.co/spaces/junk1107/ai-labor-platform → Logs

---

## 📚 详细文档

完整的部署指南请查看: `AUTO_DEPLOYMENT_GUIDE.md`

---

## 💡 提示

- 部署脚本会自动检查文件和Token
- 如果没有文件更改，会跳过提交
- GitHub Actions会在代码推送时自动部署
- 应用更新不会中断服务

---

**最后更新**: 2026-01-13

快速参考卡 - 打印或保存此页面以便快速查阅！
