## Docker Image to AWS ECR Pusher
This script simplifies the process of pushing Docker images to Amazon Elastic Container Registry (ECR) by automating all the required steps. It uses the Boto3 Python library to interact with the AWS ECR service.

## Prerequisites
* Python 3.6 or newer
* Docker installed and running
* AWS CLI installed and configured with necessary access credentials
* Boto3 installed (pip install boto3)
* AWS account with ECR access and necessary permissions

## Usage

```
python ecr_pusher.py --region <region> --imagename <imagename>


```

This script accepts two command-line arguments:

* `--region`: Required. The AWS region in which the ECR repository is to be created.
* `--imagename`: Required. The name of the Docker image you want to push to ECR.

This script will:

1. Create an ECR repository if it does not exist in the specified AWS region.
2. Authenticate Docker to the ECR registry.
3. Build a Docker image using the Dockerfile in the current directory.
4. Tag the Docker image with the repository URI and latest tag.
5. Push the Docker image to the ECR repository.


After the script finishes, it will print the Docker image URI, which you can use to reference the Docker image in the ECR repository.

## Important Note

Please make sure you have a Dockerfile in the directory from which you run this script. The Dockerfile should contain instructions for building your Docker image. The `docker build `command in this script will look for a Dockerfile in the current directory.