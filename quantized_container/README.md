# llama.cpp Compatible Quantized Model API

## Overview

This directory contains a Dockerized application that serves a Llama model for text generation via a FastAPI server. The server offers a POST `/invoke` endpoint for generating text and a POST `/configure` endpoint for configuring the model. 

## Requirements

You will need to have Docker installed on your machine. 

Download Docker here: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

## Building the Docker Image

You can build the Docker image by running the following command in the `quantized_container` directory:

```sh
docker build -t <IMAGE_NAME> .
```

Replace `<IMAGE_NAME>` with the name you want to give to your Docker image.

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
        "model_path": "<MODEL_PATH>",
        "n_ctx": 512,
        "n_parts": -1,
        // ... include other configuration parameters as needed ...
    }
}'


```

Replace` <MODEL_PATH>` with the path to your Llama model. You can also adjust the other configuration parameters as needed.

### Generating Text

To generate text, make a POST request to `/invoke` with a JSON payload. Here is an example using curl:

```

curl --location --request POST 'http://localhost:8080/invoke' \
--header 'Content-Type: application/json' \
--data-raw '{
    "configure": false,
    "inference": true,
    "args": {
        "prompt": "<YOUR_PROMPT>",
        "max_tokens": 128,
        "temperature": 0.7,
        // ... include other generation parameters as needed ...
    }
}'


```

Replace `<YOUR_PROMPT>` with the prompt you want to generate text from. You can also adjust the other generation parameters as needed.

## Miscellaneous

To check if the server is running, you can make a GET request to` /ping.` If the server is running, it will return a 200 status code. Here is an example using curl:

```

curl --location --request GET 'http://localhost:8080/ping'


```

This command should return `OK` if the server is running.


Please replace the parts like `<MODEL_PATH>` or `<YOUR_PROMPT>` with your specific data.
