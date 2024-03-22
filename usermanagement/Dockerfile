# Use an official Python runtime as the parent image
FROM public.ecr.aws/docker/library/python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y nginx 

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/

# Install any Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./src /app/

# Copy Nginx configuration file
COPY ./config/nginx.conf /etc/nginx/nginx.conf

# Make port 80 and 443 available to the world outside this container
EXPOSE 80 443

# Define environment variable to tell Flask to run in production mode
ENV FLASK_ENV=production

# Start Nginx and the Flask application
CMD ["sh", "-c", "nginx && flask run --host=0.0.0.0 --port=80"]