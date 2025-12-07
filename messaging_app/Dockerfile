# Use a base Python image python:3.10
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install necessary dependencies from the Requirements.txt
COPY Requirements.txt /app/Requirements.txt
RUN pip install --upgrade pip
RUN pip install -r Requirements.txt

# Copy your app code into the container
COPY . /app/

# Expose the port your Django app runs on (default is 8000)
EXPOSE 8000

# Run the application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
