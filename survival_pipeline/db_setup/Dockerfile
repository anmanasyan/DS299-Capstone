# Use Python 3.10 Alpine image as base
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Update package index and install necessary packages
RUN apk update && \
    apk add --no-cache postgresql-dev gcc python3-dev musl-dev bash

# Set working directory
WORKDIR /db_setup

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt 
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 3000
EXPOSE 3000

# Command to run the python file
CMD ["python", "data_ingest.py"]
