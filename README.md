# _Lollipop on Cloud_ for On-Demand User Requests

![WIP](https://img.shields.io/badge/status-WIP-yellow)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0.1-blue)
![Docker](https://img.shields.io/badge/docker-19.03.12-blue)
![AWS S3](https://img.shields.io/badge/AWS%20S3-Cloud-orange)

This package takes Lollipop, a tool used in V-Pipe's post-processing, and containerizes it to be run on-demand. This is part of the effort "V-Pipe on Cloud".

## Overview

Lollipop is a powerful tool used in V-Pipe's post-processing pipeline. This project aims to containerize Lollipop, allowing it to be run on-demand via a Flask-based API. This enables users to perform deconvolution tasks on-demand, leveraging the power of cloud computing.

## _V-Pipe on Cloud_

This project is part of the "V-Pipe on Cloud" initiative, which aims to bring the capabilities of V-Pipe to the cloud, making it more accessible and scalable.

For more information about V-Pipe, visit the [V-Pipe website](https://cbg-ethz.github.io/V-pipe/).

## Tech Stack

- **Python**: The core programming language used for the project.
- **Flask**: A lightweight WSGI web application framework used to create the web server.
- **Docker**: Used to containerize the application, ensuring consistency across different environments.
- **AWS S3**: Used for storing and retrieving data files.

## Work in Progress

This project is a work in progress and is being actively developed. Contributions and feedback are welcome.

## Hackathon Project

This project was initiated as part of a hackathon project at the [BioHackathon Europe 2024](https://biohackathon-europe.org/).

## Related Repositories

This repository relates to the front-end at [vpipe-biohack24-frontend](https://github.com/cbg-ethz/vpipe-biohack24-frontend).

## Deployment

The current deployment of this project can be accessed at [biohack24.g15n.net](http://biohack24.g15n.net).

## Getting Started

### Prerequisites

- Docker
- AWS credentials with access to the required S3 buckets

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/cbg-ethz/lollipop-in-cloud.git
    cd lollipop-in-cloud
    ```

2. Build the Docker image:
    ```sh
    docker build -t lollipop-in-cloud .
    ```

3. Run the Docker container:
    ```sh
    docker run --env-file .env -p 8000:8000 lollipop-in-cloud
    ```

4. Access the API:
    The API will be running at `http://localhost:8000`.

### Configuration

Ensure you have a `.env` file with the following content:
