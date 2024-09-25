# Use the official Python base image
FROM python:3.10-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt /app/

# Install the required Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port if needed (for your application it might not be necessary since you're using Telegram API)
# EXPOSE 5000 (commented as you don't expose anything to the web directly)

# Set the default command to run your bot
CMD ["python3", "bot.py"]
