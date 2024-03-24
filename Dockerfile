# Use the official Python image from Docker Hub
FROM python:3.9.6

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /ins-crawler-container

# Copy the requirements file into the container at /app
COPY requirements.txt /ins-crawler-container/
COPY Makefile /ins-crawler-container/

# Install any dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /ins-crawler-container/

# Run the main.py script
CMD ["python3 ", "main.py"]
