# 基于官方 Python slim 镜像
FROM python:3.11-slim

# 环境
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安装系统依赖（如果需要额外依赖，可在此添加）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# 复制依赖并安装
# 请确保 backend/requirements.txt 存在并列出 uvicorn、fastapi、sqlalchemy 等依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./

# 暴露端口（与项目默认端口一致）
EXPOSE 8000

# 使用仓库启动脚本，run.py 会读取 config.Settings（来自 .env）
# 生产环境请自行配置 workers（例如使用 gunicorn + uvicorn workers）
CMD ["python", "run.py"]