from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import io
import base64
import os
from dotenv import load_dotenv
import subprocess
import pandas as pd
import boto3
import uuid
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create an S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

app = Flask(__name__)

def download_from_s3(bucket_name, s3_key, local_path):
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        logging.info(f"Downloaded {s3_key} from {bucket_name} to {local_path}")
    except Exception as e:
        logging.error(f"Error downloading {s3_key} from {bucket_name}: {e}")

def generate_plot_from_csv(csv_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Create the plot
    plt.figure(figsize=(10, 6))

    plt.plot(df['date'], df['value'])  # Adjust columns as needed
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Deconvolved Data Plot')

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url

@app.route('/run_lollipop', methods=['POST'])
def run_lollipop():
    data = request.json
    yaml_data = data['yaml']

    # Create a unique directory for this request
    request_id = str(uuid.uuid4())
    local_dir = f'/tmp/lollipop_run_{request_id}'
    os.makedirs(local_dir, exist_ok=True)

    # Save the YAML data to a file
    yaml_path = os.path.join(local_dir,'var_dates.yaml')
    with open(yaml_path, 'w') as file:
        file.write(yaml_data)

    # Define S3 bucket and keys
    bucket_name = 'vpipe-output'
    s3_files = {
        'tallymut.tsv.zst': 'tallymut.tsv.zst',
        'variant_config.yaml': 'variant_config.yaml',
        'deconv_bootstrap_cowwid.yaml': 'deconv_bootstrap_cowwid.yaml',
        'filters_badmut.yaml': 'filters_badmut.yaml',
        'ww_locations.tsv': 'ww_locations.tsv'
    }
    # Download files from S3
    for local_file, s3_key in s3_files.items():
        local_path = os.path.join(local_dir, local_file)
        logging.info(f"Downloading {s3_key} to {local_path}...")
        download_from_s3(bucket_name, s3_key, local_path)
        logging.info(f"Downloaded {s3_key} to {local_path}")

    # Run lollipop deconvolute command
    location = data.get('location', '')
    command = [
        'lollipop', 'deconvolute', f'{local_dir}/tallymut.tsv.zst',
        '--variants-config', f'{local_dir}/variant_config.yaml',
        '--variants-dates', yaml_path,
        '--deconv-config', f'{local_dir}/deconv_bootstrap_cowwid.yaml',
        '--filters', f'{local_dir}/filters_badmut.yaml',
        '--seed=42',
        '--n-cores=1',
        f'--location={location}',
        '--output', f'{local_dir}/deconvolved.csv'
    ]
    subprocess.run(command, check=True)

    # Generate the plot from the output file
    output_file_path = os.path.join(local_dir, 'deconvolved.csv')
    plot_url = generate_plot_from_csv(output_file_path)

    return jsonify({'plot_url': f'data:image/png;base64,{plot_url}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

