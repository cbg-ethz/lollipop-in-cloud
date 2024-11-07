import boto3
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

def download_from_s3(bucket_name, s3_key, local_path):
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        logging.info(f"Downloaded {s3_key} from {bucket_name} to {local_path}")
    except Exception as e:
        logging.error(f"Error downloading {s3_key} from {bucket_name}: {e}")