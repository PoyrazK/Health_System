# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (if any needed for numpy/pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and models
# Assuming build context is project root
COPY src /app/src
COPY models /app/models

# Expose the port
EXPOSE 8000

# Command to run the application
# Use shell form to allow variable expansion if needed, but array form is safer for signals
CMD ["uvicorn", "src.api.ml_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
