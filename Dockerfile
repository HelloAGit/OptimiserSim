# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system/build dependencies required for some Python packages (numpy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libop## Solution for Failing Docker Build Job

The job is failing because **`libatlas-base-dev` is not available in the ARM64 (linux/arm64) build environment**. This packageenblas-dev \
    libblas-dev \
    liblapack-dev \
    libffi-dev \
    libssl-dev \
    ca- `linux/amd64` and `linux/arm64` platforms:
