import boto3
import subprocess
import os
import argparse

def create_ecr_repository(image_name, region):
    client = boto3.client('ecr', region_name=region)

    try:
        response = client.describe_repositories(repositoryNames=[image_name])
    except client.exceptions.RepositoryNotFoundException:
        response = client.create_repository(repositoryName=image_name)

    return response['repositories'][0]['repositoryUri']

def get_docker_login_cmd(region):
    client = boto3.client('ecr', region_name=region)
    response = client.get_authorization_token()

    username, password = (
        boto3.utils.base64_decode(response['authorizationData'][0]['authorizationToken']).split(b':')
    )

    return f"docker login -u {username.decode()} -p {password.decode()} https://{response['authorizationData'][0]['proxyEndpoint']}"


def main():
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description='Push Docker image to ECR')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--imagename', required=True, help='Docker image name')

    args = parser.parse_args()
    region = args.region
    image_name = args.imagename

    # Create an ECR repository and get the repository URI
    repository_uri = create_ecr_repository(image_name, region)

    # Get the Docker login command
    docker_login_cmd = get_docker_login_cmd(region)

    # Use subprocess to execute the Docker login command
    subprocess.run(docker_login_cmd, shell=True)

    # Build, tag, and push your Docker image
    # Note that you would need to replace <local-image> and <image-tag> with your actual local image name and tag
    docker_build_cmd = f"docker build -t {image_name} ."
    docker_tag_cmd = f"docker tag {image_name}:latest {repository_uri}:latest"
    docker_push_cmd = f"docker push {repository_uri}:latest"

    subprocess.run(docker_build_cmd, shell=True)
    subprocess.run(docker_tag_cmd, shell=True)
    subprocess.run(docker_push_cmd, shell=True)

    # At this point, your Docker image is pushed to ECR and you have your image URI
    print(f"Docker image URI: {repository_uri}:latest")

if __name__ == "__main__":
    main()