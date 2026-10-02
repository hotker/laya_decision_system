FROM python:3.12-slim

WORKDIR /app

# Build dependency
RUN pip install --no-cache-dir setuptools

# Install project (includes core + dev dependencies)
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# Copy code
COPY . .

# Output directory
RUN mkdir -p output

# Default command
CMD ["python", "src/main.py"]