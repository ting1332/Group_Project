   # 使用官方 Python 作为基础镜像
   FROM python:3.9-slim

   # 设置工作目录
   WORKDIR /app

   # 复制 requirements.txt 并安装依赖项
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # 复制应用程序代码
   COPY . .

   # 指定容器启动时运行的命令
   CMD ["python", "groupwork.py"]