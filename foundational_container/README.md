# Huggingface Compatible Foundation Model API

## Overview

This directory contains a Dockerized application that serves a HuggingFace model for text generation via a FastAPI server. The server offers a POST `/invoke` endpoint for generating text and a POST `/configure` endpoint for configuring the model. 

## Requirements

You will need to have Docker installed on your machine. 

Download Docker here: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

## Building the Docker Image

You can build the Docker image by running the following command in the directory that contains the Dockerfile:

```sh
docker build -t <IMAGE_NAME> --build-arg MODEL=<MODEL_NAME> --build-arg HF_TOKEN=<HUGGINGFACE_TOKEN> .
```

Replace `<IMAGE_NAME>` with the name you want to give to your Docker image, `<MODEL_NAME>` with the HuggingFace model name, and `<HUGGINGFACE_TOKEN> `with your HuggingFace API token.

## Running the Docker Container

You can run the Docker container by running the following command:

```

docker run -p 8080:8080 <IMAGE_NAME>


```

Replace `<IMAGE_NAME>` with the name of your Docker image. This command runs the Docker container and maps the container's port 8080 to your machine's port 8080.

## Using the FastAPI Server

Once the Docker container is running, you can interact with the FastAPI server.

### Configuring the Model

To configure the model, make a POST request to `/configure` with a JSON payload. Here is an example using curl:

```

curl --location --request POST 'http://localhost:8080/configure' \
--header 'Content-Type: application/json' \
--data-raw '{
    "configure": true,
    "inference": false,
    "args": {
        "pretrained_model_name_or_path": "<MODEL_NAME>",
        "use_auth_token": "<HUGGINGFACE_TOKEN>"
    }
}'



```
Replace` <MODEL_NAME>` with the HuggingFace model name and `<HUGGINGFACE_TOKEN>` with your HuggingFace API token.

### Generating Text

To generate text, make a POST request to `/invoke` with a JSON payload. Here is an example using curl:

```
curl --location --request POST 'http://localhost:8080/invoke' \
--header 'Content-Type: application/json' \
--data-raw '{
    "configure": false,
    "inference": true,
    "args": {
        "input_text": "<YOUR_INPUT_TEXT>"
    }
}'

```

## Miscellaneous

To check if the server is running, you can make a GET request to `/ping`. If the server is running, it will return a 200 status code. Here is an example using curl:

```
curl --location --request GET 'http://localhost:8080/ping'

```

This command should return `OK` if the server is running.




