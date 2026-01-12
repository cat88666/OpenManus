# 部署指南

## 目录
1. [本地开发](#本地开发)
2. [Docker部署](#docker部署)
3. [生产环境部署](#生产环境部署)
4. [监控和维护](#监控和维护)

## 本地开发

### 前置要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/cat88666/OpenManus.git
cd OpenManus/platform
```

#### 2. 配置环境变量
```bash
# 后端
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入API密钥

# 前端
cp frontend/.env.example frontend/.env
```

#### 3. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

访问 API: http://localhost:8000
API文档: http://localhost:8000/docs

#### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

访问应用: http://localhost:3000

#### 5. 启动Streamlit仪表板
```bash
cd streamlit-dashboard
pip install -r requirements.txt
streamlit run app.py
```

访问仪表板: http://localhost:8501

## Docker部署

### 使用Docker Compose

#### 1. 构建镜像
```bash
docker-compose build
```

#### 2. 启动服务
```bash
docker-compose up -d
```

#### 3. 查看日志
```bash
docker-compose logs -f backend
docker-compose logs -f streamlit
```

#### 4. 停止服务
```bash
docker-compose down
```

### 服务访问
- API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Streamlit: http://localhost:8501
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 生产环境部署

### 使用Kubernetes

#### 1. 创建命名空间
```bash
kubectl create namespace ai-labor
```

#### 2. 创建ConfigMap和Secret
```bash
kubectl create configmap ai-labor-config \
  --from-file=backend/.env \
  -n ai-labor

kubectl create secret generic ai-labor-secret \
  --from-literal=db-password=your-secure-password \
  --from-literal=redis-password=your-secure-password \
  -n ai-labor
```

#### 3. 部署应用
```bash
kubectl apply -f k8s/
```

#### 4. 检查部署状态
```bash
kubectl get pods -n ai-labor
kubectl get svc -n ai-labor
```

### 使用Nginx反向代理

#### nginx.conf 示例
```nginx
upstream backend {
    server backend:8000;
}

upstream streamlit {
    server streamlit:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;

    # API代理
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 前端
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Streamlit
    location /dashboard/ {
        proxy_pass http://streamlit/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 数据库迁移

#### 初始化数据库
```bash
cd backend
python -c "from database import init_db; init_db()"
```

#### 备份数据库
```bash
pg_dump -U admin ai_labor > backup.sql
```

#### 恢复数据库
```bash
psql -U admin ai_labor < backup.sql
```

## 监控和维护

### 日志管理

#### 查看日志
```bash
# Docker
docker-compose logs backend

# Kubernetes
kubectl logs -f deployment/backend -n ai-labor
```

#### 日志级别配置
在 `.env` 中设置:
```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 性能监控

#### 使用Prometheus和Grafana
```bash
# 启动Prometheus
docker run -d -p 9090:9090 -v prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

# 启动Grafana
docker run -d -p 3000:3000 grafana/grafana
```

#### 添加监控指标
在 `main.py` 中添加:
```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

### 备份策略

#### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ai-labor"

# 备份数据库
pg_dump -U admin ai_labor | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份知识库
tar -czf $BACKUP_DIR/knowledge_base_$DATE.tar.gz /app/knowledge_base

# 上传到S3
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-bucket/backups/

# 清理旧备份（保留7天）
find $BACKUP_DIR -mtime +7 -delete
```

#### 定时执行备份
```bash
# 添加到crontab
0 2 * * * /path/to/backup.sh
```

### 健康检查

#### API健康检查
```bash
curl http://localhost:8000/health
```

#### 数据库连接检查
```python
# 在应用启动时检查
from database import engine
try:
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    logger.info("Database connection OK")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
```

### 更新和升级

#### 更新依赖
```bash
cd backend
pip install --upgrade -r requirements.txt

cd ../frontend
npm update
```

#### 版本管理
```bash
# 标记版本
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 查看版本
git tag -l
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查连接字符串
echo $DATABASE_URL

# 测试连接
psql $DATABASE_URL -c "SELECT 1"
```

#### 2. Redis连接失败
```bash
# 检查Redis状态
redis-cli ping

# 查看Redis配置
redis-cli CONFIG GET "*"
```

#### 3. API响应缓慢
```bash
# 检查API日志
docker-compose logs backend | grep "duration"

# 检查数据库查询性能
# 在PostgreSQL中启用查询日志
```

### 调试模式

#### 启用调试日志
```bash
# 在 .env 中设置
DEBUG=True
LOG_LEVEL=DEBUG
```

#### 使用pdb调试
```python
import pdb
pdb.set_trace()
```

## 性能优化

### 数据库优化
- 添加索引到常用查询字段
- 使用连接池
- 定期清理过期数据

### 缓存策略
- 使用Redis缓存热数据
- 实现缓存预热
- 设置合理的过期时间

### 代码优化
- 使用异步操作
- 实现分页查询
- 使用批量操作

---

**最后更新**: 2026-01-13
**版本**: v1.0
