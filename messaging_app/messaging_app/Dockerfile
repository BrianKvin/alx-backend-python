# Use official Python 3.10 base image
FROM python:3.10

# Set working directory inside container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code into the container
COPY . .

# Expose the port your Django app runs on
EXPOSE 8000

# Default command to run your Django app (adjust if using something else)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
