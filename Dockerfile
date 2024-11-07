FROM quay.io/biocontainers/lollipop:0.5.0--pyhdfd78af_0

# Set the working directory
WORKDIR /app

# Copy additional project files
COPY requirements.txt ./
COPY app.py ./
COPY .env ./

# Install additional Python dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the Flask app
CMD ["python", "app.py"]