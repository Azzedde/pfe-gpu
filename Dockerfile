# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential procps \
    && apt-get clean

# Install python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# Expose the Django app port
EXPOSE 8000

# Run the application
CMD ["python", "./pfe_gpu_form/manage.py", "runserver", "0.0.0.0:8000"]
