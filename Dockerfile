# 使用 Python 3.9 作為基礎映像
FROM --platform=linux/amd64 python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製需求文件
COPY requirements.txt web.py ./

# 複製靜態檔案
COPY index.html ./static/

# 安裝需求
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8080

# 設定啟動命令
CMD ["python", "web.py"]
