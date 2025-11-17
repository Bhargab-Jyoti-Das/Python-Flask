# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first, to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Set environment variable to prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Start the Flask app
CMD ["python", "app.py"]
