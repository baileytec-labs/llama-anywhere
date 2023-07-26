import argparse
import subprocess
import boto3

def list_instance_types(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)
    instance_types = []

    paginator = ec2.get_paginator('describe_instance_types')
    for page in paginator.paginate():
        for instance_type in page['InstanceTypes']:
            if instance_type['MemoryInfo']['SizeInMiB'] >= 6 * 1024: #Based on my testing with Lambda, it's going to be useless to even try the quantized models on architecture smaller than 6GB.
                instance_types.append(instance_type['InstanceType'])

    return instance_types

def run_shell_script(deploytype, port, model, instance_type):
    command = ["bash", "end2endtest.sh", 
               "-deploytype", deploytype, 
               "-port", str(port), 
               "-model", model, 
               "-instancetype", instance_type]
    subprocess.check_call(command)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("foundationmodel",required=False, type=str,default="VMware/open-llama-7b-v2-open-instruct", help="Huggingface transformer compatible repository path (VMware/open-llama-7b-v2-open-instruct)")
    parser.add_argument("quantizedmodel", required=False, type=str,default="https://huggingface.co/TheBloke/open-llama-7B-v2-open-instruct-GGML/resolve/main/open-llama-7b-v2-open-instruct.ggmlv3.q2_K.bin",help="URL or path to the quantized model (https://huggingface.co/TheBloke/open-llama-7B-v2-open-instruct-GGML/resolve/main/open-llama-7b-v2-open-instruct.ggmlv3.q2_K.bin)")
    parser.add_argument("instancetype",type=str,default="multi",required=False, help="If you'd like to just have a single instance type to test the two models against, specify it here. Otherwise it will cycle through all instances." )
    args = parser.parse_args()
    port = 8080
    if args.instancetype == "multi":
        instance_types = list_instance_types('us-east-1') 
    else:
        instance_types=[args.instancetype]

    for instance_type in instance_types:
        # Run shell script for foundation model
        run_shell_script('f', port, args.foundationmodel, instance_type)

        # Run shell script for quantized model
        run_shell_script('q', port, args.quantizedmodel, instance_type)

if __name__ == '__main__':
    main()
