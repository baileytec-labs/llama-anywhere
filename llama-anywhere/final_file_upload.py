import boto3
import os
import threading
import boto3
from botocore.exceptions import NoCredentialsError
from tqdm import tqdm
import requests
import json
import argparse
import traceback
import logging
import time

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
        if output['OutputKey'] == 'QuantizedInstancePublicIP':
            return output['OutputValue']

    # If the output key was not found, return None
    return None


def is_url(path):
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

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

#You know what, it would be better / simpler if we did not have both things running in parallel. Cheaper, faster to deploy, etc.
#Essentially, we only need to change the userdata based on if the input is for a quantized model or for a foundation model. 
#Keep everything downstream standardized.

#We need stackname, port, deploytype, model, instance type. 
#We need to check and see if it's a local file or a url if the thing is quantized
#
def main():
    parser = argparse.ArgumentParser(description="Some description about your program")

    # add arguments
    parser.add_argument("--stackname", default='llama-anywhere', help="The name of the stack")
    parser.add_argument("--port", default='8080', help="The port to use")
    parser.add_argument("--context", default=2048, type=int, help="Context")
    parser.add_argument("--tokenresponse", default=512, type=int, help="Token response")

    # parse the arguments
    args = parser.parse_args()
    STACKNAME = args.stackname
    port = args.port
    CONTEXT = args.context
    TOKENRESPONSE = args.tokenresponse
    #LOCALMODEL="/Users/seanbailey/Github/llama-anywhere/llama2-testmodel.bin" #we pull this from the cloudformation stack.
    # Invocation payload needs to be standardized and pulled from a file of some sort.
    
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
    selectedmodel = next((item for item in outputs if item["OutputKey"] == "ObjectName"), None)
    deploytype=next((item for item in outputs if item["OutputKey"] == "DeployType"), None)
    instanceprice=next((item for item in outputs if item["OutputKey"] == "InstancePrice"), None)
    instancetype=next((item for item in outputs if item["OutputKey"] == "InstanceType"), None)
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
    config_payload={}
    invoke_payload = {
        "prompt": "Context: In a small town named Grandville, a well-known millionaire, Mr. Smith, has been mysteriously murdered at his mansion. No one has been able to solve the case yet. Detective Anderson, an old friend of Mr. Smith, has taken it upon himself to solve this case. Detective Anderson was just informed that Mr. Smith had received a strange letter the day before his death. Prompt: You are now the character of Detective Anderson. Here's what you need to do in this exercise: 1. Start by expressing your feelings about Mr. Smith's death to the local sheriff, considering your old friendship with him. 2. Then, ask the sheriff about the details of this strange letter. 3. Finally, suggest a theory about the possible connection between this letter and Mr. Smith's death, and propose your next steps in the investigation. ",
        
    }
    if 'Q' in deploytype.upper():
        if not is_url(selectedmodel):

            multipart_upload_with_s3(selectedmodel, bucket_name, selectedmodel.split("/")[-1])

            logger.info("Uploaded model to s3, now testing the endpoint...")
            config_payload['bucket']=bucket_name
            config_payload['key'] = selectedmodel.split("/")[-1]
        else:
            config_payload['model_path']=selectedmodel
        
        config_payload['n_ctx']=CONTEXT
        invoke_payload['max_tokens']=TOKENRESPONSE
    if 'F' in deploytype.upper():
        #we're not uploading with S3, so it makes things easier.
        config_payload['pretrained_model_name']=selectedmodel
        invoke_payload['max_new_tokens']=TOKENSRESPONSE


    # Ping
    #we want to record the time it took to complete each response
    #we want to record the prompt
    #we want to record the response
    #we want to record the instance type
    #We want to record the on demand cost
    #We want to calculate and record the total cost. Billed at 60 second minimum durations.
    try:
        starttime=time.time()
        ping_response = requests.get(f"{public_ip}/ping")
        endtime=time.time()
        roundtrip=endtime-starttime
        if roundtrip/60 < 1:
            totalcost=1
        else:
            totalcost=roundtrip/60
        totalcost=totalcost * instanceprice
        logger.info(ping_response.status_code)  # Print the response status code
        logdict={
            "Action":"Ping response",
            "roundtrip_time":roundtrip,
            "instance_type":instancetype,
            "on_demand_cost":instanceprice,
            "total_cost":totalcost
        }
        logger.info(json.dumps(logdict))
    except:
        logdict={
            "Action":"Ping response",
            "error_message":str(traceback.format_exc()),
            "instance_type":instancetype,
        }
        logger.info(json.dumps(logdict))

    #We're going to need some form of standardized configuration payload settings...


    try:
        starttime=time.time()
        config_response = requests.post(f"{public_ip}/configure", data=json.dumps(config_payload))
        #logger.info(config_response.json())  # Print the response from the server
        endtime=time.time()
        roundtrip=endtime-starttime
        if roundtrip/60 < 1:
            totalcost=1
        else:
            totalcost=roundtrip/60
        totalcost=totalcost * instanceprice
        logger.info(ping_response.status_code)  # Print the response status code
        logdict={
            "Action":"Configuration",
            "roundtrip_time":roundtrip,
            "instance_type":instancetype,
            "on_demand_cost":instanceprice,
            "total_cost":totalcost,
        }
        config_data=config_response.json()
        logdict.update(config_data)
        logdict.update(config_payload)
        logger.info(json.dumps(logdict))
    except:
        logdict={
            "Action":"Configuration",
            "error_message":str(traceback.format_exc()),
            "instance_type":instancetype,
        }
        logdict.update(config_payload)
        logger.info(json.dumps(logdict))

    try:
        starttime=time.time()
        invoke_response = requests.post(f"{public_ip}/invoke", data=json.dumps(invoke_payload))
        #logger.info(invoke_response.json())  # Print the response from the server
        endtime=time.time()
        roundtrip=endtime-starttime
        if roundtrip/60 < 1:
            totalcost=1
        else:
            totalcost=roundtrip/60
        totalcost=totalcost * instanceprice
        logger.info(ping_response.status_code)  # Print the response status code
        logdict={
            "Action":"Invocation",
            "roundtrip_time":roundtrip,
            "instance_type":instancetype,
            "on_demand_cost":instanceprice,
            "total_cost":totalcost,
        }
        invoke_data=invoke_response.json()
        logdict.update(invoke_data)
        logdict.update(invoke_payload)
        logger.info(json.dumps(logdict))
    except:
        logdict={
            "Action":"Configuration",
            "error_message":str(traceback.format_exc()),
            "instance_type":instancetype,
        }
        logdict.update(invoke_payload)
        logger.info(json.dumps(logdict))


    
if __name__ == "__main__":
    main()



    

#I need to modify this file to make it more modular and put in functions, and have it run in parallel for testing both the quantized and the non-quantized deployments. 
#It needs to record even if there is a timeout (failure to the instance or whatever)
#It needs to write the information that it is prompting each endpoint with / the configurations of those models
#It needs to record the time it takes to perform inference
#It needs to record the cost of that inference
#It needs to record the output of each model.