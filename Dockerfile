FROM prefecthq/prefect:3.3.7-python3.12

# Set working directory
WORKDIR /app

# Install additional dependencies directly with pip
RUN pip install boto3>=1.34.0

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Default command
CMD ["prefect", "worker", "start", "-p", "my-k8s-pool"] 