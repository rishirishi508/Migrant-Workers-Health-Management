# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app.py .
COPY utils/ ./utils/
COPY templates/ ./templates/

# Expose the app port (Flask default 5000)
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
