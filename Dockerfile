FROM prefecthq/prefect:3.3.7-python3.12

# Install poetry
RUN pip install poetry

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Set working directory
WORKDIR /app

# Copy poetry files
COPY pyproject.toml ./

# Install dependencies
RUN poetry install --only=main --no-dev

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Default command
CMD ["prefect", "worker", "start", "-p", "my-k8s-pool"] 