# Use the official Python image as a base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8001

# Start the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
