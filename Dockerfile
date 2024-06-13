# 使用 Python 3.9 作為基礎映像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製需求文件
COPY requirements.txt .

# 安裝需求
RUN pip install --no-cache-dir -r requirements.txt

# 創建上傳目錄
RUN mkdir -p /tmp

# 設置目錄權限
RUN chmod -R 777 /tmp

# 複製應用程式代碼
COPY . .

# 複製靜態檔案
COPY index.html ./static/

# 暴露端口
EXPOSE 8080

# 設定啟動命令
CMD ["python", "web2.py"]
