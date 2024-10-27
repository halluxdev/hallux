# Copyright: Hallux team, 2024

# Dockerfile example
# to build run:
#   ./scripts/build-package.sh
#   docker build -t hallux-image .

# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables to avoid cache issues and ensure repeatable builds
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Upgrade pip and install project specific modules
RUN pip install --upgrade pip \
  pytest==8.3.3 \
  pytest-cov==5.0.0 \
  ruff==0.0.272

# Install make and git to be able to run validity tests
RUN apt-get update && \
  apt-get install -y make git && \
  rm -rf /var/lib/apt/lists/*

# Copy the wheel file from the host machine to the container
COPY ./dist/*.whl /app/

# Install the wheel file
RUN pip install /app/*.whl

# Set the entrypoint to hallux
ENTRYPOINT ["hallux"]

# Example of how to run hallux from this Docker image:
# docker run --rm -it hallux-image --help
# docker run --rm -it -v $(pwd):/app -e LOG_LEVEL=DEBUG hallux-image --sonar --model=ollama/llama3.2 .

# Run bash inside the image
# docker run --rm -it --entrypoint /bin/bash -v $(pwd):/app hallux-image


