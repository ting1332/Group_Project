# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 先复制 requirements.txt
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录内容到容器中的 /app 目录
COPY . .

# 使容器在启动时运行 groupwork.py
CMD ["python", "groupwork.py"]
