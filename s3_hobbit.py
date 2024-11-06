import boto3
import os
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
load_dotenv()

def download_from_s3(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_path)

def upload_to_s3(bucket_name, local_path, s3_key):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, bucket_name, s3_key)

# Example usage
bucket_name = 'vpipe-output'
s3_files = {
    'tallymut.tsv': 'path/to/input/tallymut.tsv',
    'variant_config.yaml': 'path/to/input/variant_config.yaml',
    'var_dates.yaml': 'path/to/input/var_dates.yaml',
    'deconv_bootstrap_cowwid.yaml': 'path/to/input/deconv_bootstrap_cowwid.yaml',
    'filters_badmut.yaml': 'path/to/input/filters_badmut.yaml'
}
local_dir = '/tmp/lollipop_test'

# Create local directory if it doesn't exist
os.makedirs(local_dir, exist_ok=True)

# Download files from S3
for local_file, s3_key in s3_files.items():
    local_path = os.path.join(local_dir, local_file)
    download_from_s3(bucket_name, s3_key, local_path)

# Run lollipop deconvolute command
ldata = local_dir
command = [
    'lollipop', 'deconvolute', f'{ldata}/tallymut.tsv',
    '--variants-config', f'{ldata}/variant_config.yaml',
    '--variants-dates', f'{ldata}/var_dates.yaml',
    '--deconv-config', f'{ldata}/deconv_bootstrap_cowwid.yaml',
    '--filters', f'{ldata}/filters_badmut.yaml',
    '--seed=42',
    '--n-cores=3'
]
subprocess.run(command, check=True)

# Upload output file to S3 (if needed)
output_s3_key = 'path/to/output/file'
local_output_path = '/tmp/output_file'
upload_to_s3(bucket_name, local_output_path, output_s3_key)