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

@app.route('/plot', methods=['POST'])
def plot():
    data = request.json
    x = data['x']
    y = data['y']

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Sample Plot')

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return jsonify({'plot_url': f'data:image/png;base64,{plot_url}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)