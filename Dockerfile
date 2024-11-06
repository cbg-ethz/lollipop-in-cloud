FROM quay.io/biocontainers/lollipop:0.5.0--pyhdfd78af_0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy additional project files
COPY requirements.txt ./
COPY run_lollipop.py ./
COPY app.py ./
COPY .env ./

# Install additional dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the Flask app
CMD ["python", "app.py"]