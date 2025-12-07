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

# Copy requirements.txt file
COPY requirements.txt /app/

# Install necessary dependencies from the requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your app code into the container
COPY . /app/

# Expose the port your Django app runs on (default is 8000)
# To run: docker run -p 8000:8000 messaging-app
EXPOSE 8000

# Run the application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
