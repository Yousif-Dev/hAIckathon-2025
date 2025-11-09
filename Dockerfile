FROM python:3.11-slim

WORKDIR /app

# Install uv via pip
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies using uv
RUN uv sync

# Expose port for FastAPI
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the FastAPI application
CMD ["uv", "run", "uvicorn", "src.backend_api.fast_api_server:app", "--host", "0.0.0.0"]
