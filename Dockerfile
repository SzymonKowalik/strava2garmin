FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ./utils/ ./utils/
COPY ./sync.py .

# Run python script periodically every hour
CMD ["bash", "-c", "while true; do python -u sync.py; echo 'Sleeping for 1 hour...'; sleep 3600; done"]
