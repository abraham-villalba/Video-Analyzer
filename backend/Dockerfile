FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install and update dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements and application code
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

CMD ["python", "run.py"]