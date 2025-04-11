# FrontEnd dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install and update dependencies
RUN apt-get update

# Copy the requirements and application code
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0"]