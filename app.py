import subprocess
import pandas as pd
import boto3
import uuid
import logging
from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import io
import base64
import os
from dotenv import load_dotenv
import seaborn as sns
import shutil

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

def generate_plot_from_csv(csv_path, location=''):
    # Read the CSV file into a DataFrame
    data = pd.read_csv(csv_path, sep='\t')
    data['date'] = pd.to_datetime(data['date'])

    # Set the style
    sns.set_theme(style="whitegrid")

    # Sort the data by date
    data = data.sort_values(by='date')

    # Create the line plot with error bands
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=data, x='date', y='proportion', hue='variant', errorbar=None)

    # Fill the area between the lower and upper values for each variant
    for variant in data['variant'].unique():
        subset = data[data['variant'] == variant]
        plt.fill_between(subset['date'], subset['proportionLower'], subset['proportionUpper'], alpha=0.3)

    # Move the legend below the plot
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, title='Variant')
    plt.tight_layout(rect=[0, 0.1, 1, 1])  # Adjust layout to make space for the legend

    # x-axis from 0 to 1 with sensible ticks
    plt.ylim(0, 1)

    plt.xlabel('Date')
    plt.ylabel('Proportion')

    # Add a title
    plt.title('Proportion of Variants Over Time')
    # add subtitle the location variable
    plt.suptitle(f"Location: {location}")

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust layout to make space for the legend
    plt.savefig(img, format='png', bbox_inches='tight')
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
    yaml_path = os.path.join(local_dir, 'var_dates.yaml')
    with open(yaml_path, 'w') as file:
        file.write(yaml_data)

    # Define S3 bucket and keys
    bucket_name = 'vpipe-output'
    s3_files = {
        'tallymut.tsv.zst': 'tallymut.tsv.zst',
        'variant_config.yaml': 'variant_config.yaml',
        'deconv_bootstrap_cowwid.yaml': 'deconv_bootstrap_cowwid.yaml',
        'filters_badmut.yaml': 'filters_badmut.yaml',
    }

    # Download and decompress files from S3
    for local_file, s3_key in s3_files.items():
        local_path = os.path.join(local_dir, local_file)
        download_from_s3(bucket_name, s3_key, local_path)

    # Verify that all files are downloaded
    for local_file in s3_files.keys():
        local_path = os.path.join(local_dir, local_file)
        if not os.path.exists(local_path):
            logging.error(f"File not found: {local_path}")
        else:
            logging.info(f"File exists: {local_path}")

    # get the location to deconvolute for 
    location = data.get('location', '')

    # Run lollipop deconvolute command
    command = [
        'lollipop', 'deconvolute', f'{local_dir}/tallymut.tsv.zst',
        '--variants-config', f'{local_dir}/variant_config.yaml',
        '--variants-dates', yaml_path,
        '--deconv-config', f'{local_dir}/deconv_bootstrap_cowwid.yaml',
        '--filters', f'{local_dir}/filters_badmut.yaml',
        '--seed=42',
        f'--location={location}',
        '--output', f'{local_dir}/deconvolved.tsv',
        '--n-cores=1'
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running lollipop command: {e}")
        return jsonify({'error': 'Error running lollipop command'}), 500

    # Generate the plot from the output file
    output_file_path = os.path.join(local_dir, 'deconvolved.tsv')
    if not os.path.exists(output_file_path):
        logging.error(f"Output file not found: {output_file_path}")
        return jsonify({'error': 'Output file not found'}), 500

    plot_url = generate_plot_from_csv(output_file_path)

    # Clean up the local directory
    shutil.rmtree(local_dir)

    return jsonify({'plot_url': f'data:image/png;base64,{plot_url}'})

if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    app.run(host=host, port=port)

