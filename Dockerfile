FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
COPY requirements.txt .
RUN apt-get update \
    && apt-get -y install libpq-dev gcc && apt-get install -y iputils-ping
RUN pip install -r requirements.txt
# Expose the port for FastAPI
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]