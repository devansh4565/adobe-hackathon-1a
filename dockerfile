# --- Stage 1: The Builder ---
# This stage installs dependencies into a temporary location.
FROM python:3.9-slim AS builder

WORKDIR /install

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies into the target directory, not the system directory
RUN pip install --no-cache-dir --target=/install -r requirements.txt


# --- Stage 2: The Final Image ---
# This stage builds the lean, final image.
FROM python:3.9-slim

# Add the installed packages to Python's path
ENV PYTHONPATH=/install

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /install /install
# Copy the main application script
COPY main.py .

# Command to run the script automatically
CMD ["python", "main.py"]