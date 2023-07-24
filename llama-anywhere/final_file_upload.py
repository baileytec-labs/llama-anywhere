import boto3
import os
import threading
import boto3
from botocore.exceptions import NoCredentialsError
from tqdm import tqdm
import requests
import json

import logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')

# Set level of logging
logger.setLevel(logging.INFO)
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
f_format = logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

STACKNAME='llama-anywhere'
port="8080"



class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

        # Setup tqdm instance
        self._progress_bar = tqdm(
            total=self._size, 
            unit='B', 
            unit_scale=True, 
            desc=self._filename,
        )

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            # Update the progress bar
            self._progress_bar.update(bytes_amount)

    def close(self):
        self._progress_bar.close()

def get_public_ip(stack_name):
    # Create a client for the AWS CloudFormation service
    cloudformation = boto3.client('cloudformation')

    # Get the details of the stack
    stack = cloudformation.describe_stacks(StackName=stack_name)

    # Look for the output value associated with the key 'InstancePublicIP'
    for output in stack['Stacks'][0]['Outputs']:
        if output['OutputKey'] == 'InstancePublicIP':
            return output['OutputValue']

    # If the output key was not found, return None
    return None


def multipart_upload_with_s3(file_path, bucket_name, key_name):
    # Multipart upload
    config = boto3.s3.transfer.TransferConfig(
        multipart_threshold=1024 * 25, # 25MB
        max_concurrency=10,
        multipart_chunksize=1024 * 25, # 25MB
        use_threads=True
    )

    s3 = boto3.client('s3')
    progress = ProgressPercentage(file_path)

    try:
        s3.upload_file(
            file_path, bucket_name, key_name,
            Config=config,
            Callback=progress
        )
    finally:
        progress.close()

    logger.info(f"{file_path} uploaded to {bucket_name} at {key_name}")



LOCALMODEL="/Users/seanbailey/Github/llama-anywhere/llama2-testmodel.bin"

# Create a session using your current profile, or default if not provided
session = boto3.Session()

# Create a CloudFormation client
cf = session.client('cloudformation')

# Get stack details
response = cf.describe_stacks(StackName=STACKNAME)

# Extract outputs
outputs = response['Stacks'][0]['Outputs']

# Find the desired output
bucket_name = next((item for item in outputs if item["OutputKey"] == "BucketName"), None)
if bucket_name is not None:
    bucket_name = bucket_name['OutputValue']
else:
    logger.info("BucketName not found in outputs")
public_ip="http://"+get_public_ip(STACKNAME)+":"+port
# Now bucket_name contains the outputted bucket name
logger.info(bucket_name)

# Use bucket_name for your file upload operation
s3_client = session.client('s3')

#with open(LOCALMODEL, 'rb') as data:
#    s3_client.upload_fileobj(data, bucket_name, LOCALMODEL.split("/")[-1])

multipart_upload_with_s3(LOCALMODEL, bucket_name, LOCALMODEL.split("/")[-1])

logger.info("Uploaded model to s3, now testing the endpoint...")

config_payload = {
    "bucket": bucket_name,
    "key": LOCALMODEL.split("/")[-1]
}
config_response = requests.post(f"{public_ip}/configure", data=json.dumps(config_payload))
logger.info(config_response.json())  # Print the response from the server

# Ping
ping_response = requests.get(f"{public_ip}/ping")
logger.info(ping_response.status_code)  # Print the response status code

# Invocation
invoke_payload = {
    "prompt": "What is your favorite color?",
    "max_tokens": 30
}

invoke_response = requests.post(f"{public_ip}/invoke", data=json.dumps(invoke_payload))
logger.info(invoke_response.json())  # Print the response from the server

