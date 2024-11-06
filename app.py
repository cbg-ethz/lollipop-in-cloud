from flask import Flask, request, jsonify
import boto3
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def download_from_s3(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_path)

@app.route('/plot', methods=['POST'])
def plot():
    data = request.json
    start_date = data['start_date']
    end_date = data['end_date']
    bucket_name = 'your-bucket-name'
    s3_key = 'path/to/input/tallymut.tsv'
    local_path = '/tmp/tallymut.tsv'

    # Download file from S3
    download_from_s3(bucket_name, s3_key, local_path)

    # Read the file into a DataFrame
    df = pd.read_csv(local_path, sep='\t')

    # Filter the DataFrame based on the date range
    df['date'] = pd.to_datetime(df['date'])
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(filtered_df['date'], filtered_df['value'])  # Adjust columns as needed
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Filtered Data Plot')

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return jsonify({'plot_url': f'data:image/png;base64,{plot_url}'})

@app.route('/process_yaml', methods=['POST'])
def process_yaml():
    yaml_data = request.json
    # Process the YAML data as needed
    # For example, you can pass it to your existing functions
    # Here we just return it as a response for demonstration
    return jsonify({'message': 'YAML data processed successfully', 'data': yaml_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)