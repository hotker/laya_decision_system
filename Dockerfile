FROM python:3.12-slim

WORKDIR /app

# Dependencies
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# Output directory
RUN mkdir -p output

# Default command
CMD ["python", "src/main.py"]