import os
import uuid
import logging
import shutil
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from s3_utils import download_from_s3
from lollipop_utils import run_lollipop, generate_plot_from_csv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/run_lollipop', methods=['POST'])
def run_lollipop_endpoint():
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
        'filters_badmut.yaml': 'filters_badmut.yaml'
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

    # Get the location to deconvolute for
    location = data.get('location', '')

    # Run lollipop
    try:
        run_lollipop(local_dir, yaml_path, location)
    except Exception as e:
        return jsonify({'error': 'Error running lollipop command'}), 500

    # Generate the plot from the output file
    output_file_path = os.path.join(local_dir, 'deconvolved.tsv')
    if not os.path.exists(output_file_path):
        logging.error(f"Output file not found: {output_file_path}")
        return jsonify({'error': 'Output file not found'}), 500

    plot_url = generate_plot_from_csv(output_file_path, location)

    # Clean up the local directory
    shutil.rmtree(local_dir)

    return jsonify({'plot_url': f'data:image/png;base64,{plot_url}'})

if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    app.run(host=host, port=port)

