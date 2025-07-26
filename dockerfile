# Use a slim Python image for smaller size
FROM python:3.10-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by PyMuPDF
# libmupdf-dev provides the necessary MuPDF libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY main.py .

# Create input and output directories
RUN mkdir -p input output

# Command to run the application
# This command will be executed when the container starts.
# It expects PDFs in /app/input and will write JSONs to /app/output.
# The script should iterate through all PDFs in the input directory.
CMD ["python", "main.py"]