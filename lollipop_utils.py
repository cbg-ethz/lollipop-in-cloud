import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns
import logging

def run_lollipop(local_dir, yaml_path, location):
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
        raise

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