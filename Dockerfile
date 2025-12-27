# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# - libreoffice: for PPTX to PDF conversion
# - fonts-noto-cjk, fonts-noto-color-emoji: for multi-language and emoji support
# - libpq-dev, gcc: for asyncpg/PostgreSQL
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LIBREOFFICE_PATH=/usr/bin/soffice

# Command to run the bot
CMD ["python", "bot.py"]
