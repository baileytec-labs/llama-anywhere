# Llama-Anywhere: Quantized Models Performance Analysis Simplified


## Overview

Llama-Anywhere is a project inspired by the intriguing quest to understand the performance and limitations of quantized models as compared to their full-precision counterparts. With this repository, we aim to simplify and accelerate the process of benchmarking and deployment of these models.

You will find Amazon SageMaker compatible containers for any foundational model available on HuggingFace, as well as for any model that is compatible with llama.cpp. Refer to the `deploy_sagemaker_endpoint.ipynb` for detailed instructions on deploying these in SageMaker.

## Key Features


The central highlight of Llama-Anywhere is the CDK (Cloud Development Kit) code which deploys an EC2 instance, automatically setting it up with an Amazon Linux optimized AMI. It further builds and deploys a container with your selected model type, providing you with an interactive API accessible on a port you specify. You can flexibly configure your settings, prompt the model, and monitor the status of the endpoint directly from the API.

For a quick model and endpoint testing, refer to the `llama-anywhere/end2endtest.sh/ps1` file. This script automates the entire process of deployment, configuration, prompting, and teardown, logging all its results in `llama-anywhere/file.log`.

For large-scale testing, leverage `llama-anywhere/mass_test.py` which allows comparative testing between foundational and quantized models on your selected EC2 infrastructure, logging the results in `llama-anywhere/file.log`.


## Installation

Please ensure Python 3.10 or higher is installed on your system.

Clone this repository using git:

`git clone https://github.com/baileytec-labs/llama-anywhere.git`

## Usage

Once cloned, navigate to the root llama-anywhere folder. It comprises:


* `foundational_container` - Contains the Dockerfile and related code to build a Docker container with a FastAPI endpoint. This provides inference and configuration for foundational models from HuggingFace.
* `quantized_container` - Similar to the foundational_container, this contains the Dockerfile and related code for a Docker container designed for llama.cpp compatible quantized models.
* `llama-anywhere` - Contains CDK code and configurations for deploying your container to an EC2 instance, and various testing scripts.
* `deploy_sagemaker_endpoint.ipynb` - A Jupyter notebook demonstrating how to build and deploy a SageMaker endpoint using your containers.
* `put_container_in_ecr.py` - A python script facilitating the upload of your Docker container to ECR for later use in SageMaker endpoints.

Each directory contains a detailed README file for more specific instructions.

# So What?

The primary goal of Llama-Anywhere is to facilitate effortless, realistic comparisons between non-quantized and quantized models, including inference time, effects of different instance sizes and GPU capabilities, cost, etc. The Docker containers act as endpoints to perform inference in any environment, eliminating the hassle of complex configurations. This flexibility empowers users and businesses to experiment swiftly and optimize their environment to best fit their needs.


## Contributing

While this repo makes great strides at being comprehensive, it is by no means exhaustive. Any contributions are welcome to improve and expand the functionality found here. Please review the `CONTRIBUTION.md` contribution guidelines to join in on this project!