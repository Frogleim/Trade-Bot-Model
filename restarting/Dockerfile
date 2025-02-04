FROM ubuntu:20.04

# Set environment variable to avoid timezone prompt
ENV DEBIAN_FRONTEND=noninteractive

# Update and install necessary libraries and dependencies
RUN apt clean && apt update && apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    inotify-tools \
    tzdata  # Explicitly install tzdata here to ensure no prompts

# Set working directory
WORKDIR /app

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Copy project files
COPY . /app

# Install project dependencies
RUN pip3 install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Set the default command to run your app
CMD ["python3", "settings_trigger.py"]