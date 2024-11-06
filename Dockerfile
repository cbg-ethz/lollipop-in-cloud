FROM quay.io/biocontainers/lollipop:0.5.0--pyhdfd78af_0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Go back to the /app directory
WORKDIR /app

# Copy additional project files
COPY requirements.txt ./
COPY s3_hobbit.py ./
COPY .env ./

# Install additional dependencies
RUN pip install -r requirements.txt

# Run your script
CMD ["python", "s3_hobbit.py"]