# Use Python 3.10 Alpine image as base
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Update package index and install necessary packages
RUN apk update && \
    apk add --no-cache postgresql-dev gcc python3-dev musl-dev bash linux-headers

# Set working directory
WORKDIR /model

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt 
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8888 for Jupyter Notebook
EXPOSE 8888

# Command to run the python file
# CMD ["python", "generate_predictions.py"]

CMD ["bash", "-c", "python generate_predictions.py & jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token=''"]