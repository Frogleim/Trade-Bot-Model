FROM python:3.11

# Upgrade pip
RUN pip install --upgrade pip

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies and nano
RUN apt-get update \
    && apt-get -y install libpq-dev gcc iputils-ping nano \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . /app
WORKDIR /app

# Set entrypoint
ENTRYPOINT ["python3", "main.py"]