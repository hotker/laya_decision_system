FROM python:3.12-slim

WORKDIR /app

# 依赖
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 代码
COPY . .

# 输出目录
RUN mkdir -p output

# 默认命令
CMD ["python", "src/main.py"]