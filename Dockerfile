FROM prefecthq/prefect:3.3.7-python3.12

# Set working directory
WORKDIR /app

# Install uv for faster package installation
RUN pip install uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies from requirements.txt with uv (much faster than pip)
RUN uv pip install --system -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Default command
CMD ["prefect", "worker", "start", "-p", "my-k8s-pool"] 