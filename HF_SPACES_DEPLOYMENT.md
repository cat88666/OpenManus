# Hugging Face Spaces 部署指南

## 📋 目录

1. [前置要求](#前置要求)
2. [创建Spaces](#创建spaces)
3. [配置部署](#配置部署)
4. [访问应用](#访问应用)
5. [维护和更新](#维护和更新)

---

## 前置要求

### 账户要求
- Hugging Face账户（免费）
- GitHub账户（用于代码同步）

### 工具要求
- Git
- Hugging Face CLI（可选）

---

## 创建Spaces

### 步骤1：访问Hugging Face

1. 访问 https://huggingface.co
2. 登录您的账户
3. 点击头像 → "New Space"

### 步骤2：配置Space

| 选项 | 值 |
|------|-----|
| **Space名称** | ai-labor-platform |
| **License** | MIT |
| **Space SDK** | Streamlit |
| **Visibility** | Public |

### 步骤3：创建Space

点击"Create Space"按钮

---

## 配置部署

### 方法1：直接上传文件（推荐）

#### 1. 克隆Spaces仓库
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-labor-platform
cd ai-labor-platform
```

#### 2. 复制应用文件
```bash
# 复制Streamlit应用
cp /path/to/hf_spaces_app.py app.py

# 复制依赖文件
cp /path/to/requirements.txt .
```

#### 3. 创建requirements.txt
```txt
streamlit==1.28.0
pandas==2.0.0
plotly==5.17.0
requests==2.31.0
```

#### 4. 提交到Spaces
```bash
git add .
git commit -m "Initial commit: AI Labor Platform"
git push
```

### 方法2：通过GitHub同步

#### 1. 在GitHub创建仓库
```bash
# 在GitHub上创建 ai-labor-platform 仓库
```

#### 2. 推送代码
```bash
cd /path/to/OpenManus/platform
git remote add github https://github.com/YOUR_USERNAME/ai-labor-platform.git
git push github main
```

#### 3. 在Spaces中链接GitHub
1. 进入Space设置
2. 点击"Linked Repo"
3. 选择GitHub仓库
4. 启用自动同步

---

## 访问应用

### 公网访问

部署完成后，您的应用将在以下地址可访问：

```
https://huggingface.co/spaces/YOUR_USERNAME/ai-labor-platform
```

### 直接链接

Hugging Face会为您生成一个直接链接，格式如下：

```
https://YOUR_USERNAME-ai-labor-platform.hf.space
```

---

## 应用功能

### 📊 仪表板
- 实时数据展示
- 关键指标统计
- 趋势分析

### 🎯 机会管理
- 浏览机会列表
- 创建新机会
- 分析机会评分

### 📁 项目管理
- 项目列表
- 创建项目
- 进度跟踪

### 📚 知识库
- 浏览资产
- 添加新资产
- 搜索功能

### 📈 数据分析
- 关键指标
- 趋势分析
- 财务分析

### ℹ️ 关于
- 项目信息
- 技术栈
- 快速开始指南

---

## 维护和更新

### 更新应用

#### 1. 本地修改
```bash
# 修改 app.py
vim app.py

# 测试应用
streamlit run app.py
```

#### 2. 提交更改
```bash
git add app.py
git commit -m "Update: 新功能或修复"
git push
```

#### 3. Spaces自动更新
- 如果启用了GitHub同步，Spaces会自动更新
- 或者手动推送到Spaces仓库

### 查看日志

在Space页面上，您可以：
1. 点击"Logs"查看应用日志
2. 查看错误信息
3. 监控应用性能

### 性能优化

#### 1. 缓存数据
```python
@st.cache_data
def load_data():
    # 加载数据
    return data
```

#### 2. 使用列
```python
col1, col2 = st.columns(2)
with col1:
    # 内容
with col2:
    # 内容
```

#### 3. 条件渲染
```python
if condition:
    st.write("内容")
```

---

## 高级配置

### 环境变量

在Space设置中添加环境变量：

1. 进入Space设置
2. 点击"Repository secrets"
3. 添加变量，例如：
   - `API_KEY`: 您的API密钥
   - `DATABASE_URL`: 数据库连接字符串

### 使用环境变量

```python
import os

api_key = os.getenv("API_KEY")
db_url = os.getenv("DATABASE_URL")
```

### 持久化存储

Hugging Face Spaces提供临时存储。对于持久化数据：

1. 使用外部数据库
2. 使用Hugging Face Hub存储
3. 使用云存储服务

---

## 故障排除

### 应用无法启动

**问题**: Streamlit应用无法启动

**解决方案**:
1. 检查requirements.txt中的依赖
2. 查看Logs页面的错误信息
3. 确保app.py在仓库根目录

### 导入错误

**问题**: ModuleNotFoundError

**解决方案**:
1. 添加缺失的包到requirements.txt
2. 重新启动应用
3. 清除缓存

### 性能问题

**问题**: 应用响应缓慢

**解决方案**:
1. 使用@st.cache_data缓存数据
2. 优化数据加载
3. 减少不必要的计算

### 内存不足

**问题**: Out of Memory错误

**解决方案**:
1. 减少数据加载量
2. 使用分页
3. 优化数据结构

---

## 安全建议

### 1. 保护敏感信息
- 不要在代码中硬编码密钥
- 使用环境变量
- 使用Repository secrets

### 2. 输入验证
```python
if not user_input:
    st.error("输入不能为空")
    return
```

### 3. 错误处理
```python
try:
    # 代码
except Exception as e:
    st.error(f"错误: {str(e)}")
```

---

## 性能指标

### 预期性能

| 指标 | 值 |
|------|-----|
| 启动时间 | < 30秒 |
| 页面加载 | < 2秒 |
| 交互响应 | < 500ms |
| 并发用户 | 10-50 |

### 监控

在Space页面上可以查看：
- CPU使用率
- 内存使用
- 请求数
- 错误率

---

## 成本

### Hugging Face Spaces免费计划

- **CPU**: 2核
- **内存**: 16GB
- **存储**: 50GB
- **带宽**: 无限制
- **运行时间**: 无限制

### 升级选项

如需更多资源，可升级到付费计划：
- Pro: $9/月
- Enterprise: 联系销售

---

## 常见问题

### Q: 如何自定义域名？
A: Hugging Face Spaces不支持自定义域名。可以使用第三方CDN或反向代理。

### Q: 如何添加数据库？
A: 使用外部数据库服务，如：
- MongoDB Atlas
- PostgreSQL (Heroku, Railway)
- Firebase

### Q: 如何处理长时间运行的任务？
A: 使用后台任务库，如Celery或APScheduler。

### Q: 如何增加并发用户数？
A: 升级到Pro或Enterprise计划。

### Q: 如何备份数据？
A: 定期导出数据到外部存储。

---

## 下一步

### 功能扩展

1. **连接真实API**
   - 配置后端API连接
   - 添加认证
   - 实现数据同步

2. **添加用户认证**
   - 实现登录功能
   - 用户会话管理
   - 权限控制

3. **数据持久化**
   - 连接数据库
   - 实现数据存储
   - 备份策略

4. **高级功能**
   - 文件上传
   - 实时通知
   - 导出功能

---

## 相关资源

- [Hugging Face Spaces文档](https://huggingface.co/docs/hub/spaces)
- [Streamlit文档](https://docs.streamlit.io/)
- [GitHub同步指南](https://huggingface.co/docs/hub/spaces-github-actions)

---

## 支持

### 获取帮助

- Hugging Face社区: https://discuss.huggingface.co/
- Streamlit社区: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/cat88666/OpenManus/issues

---

**最后更新**: 2026-01-13  
**版本**: v1.0

---

## 快速开始命令

```bash
# 1. 克隆Spaces仓库
git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-labor-platform
cd ai-labor-platform

# 2. 复制应用文件
cp /path/to/hf_spaces_app.py app.py
cp /path/to/requirements.txt .

# 3. 本地测试
streamlit run app.py

# 4. 提交到Spaces
git add .
git commit -m "Deploy AI Labor Platform"
git push

# 5. 访问应用
# https://YOUR_USERNAME-ai-labor-platform.hf.space
```

祝您部署顺利！🚀
