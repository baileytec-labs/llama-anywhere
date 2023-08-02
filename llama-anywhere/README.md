
# Welcome to the llama-anywhere project!

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`llama_anywhere_stack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization process also creates
a virtualenv within this project, stored under the .venv directory.  To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now begin exploring the source code, contained in the hello directory.
There is also a very trivial test included that can be run like this:

```
$ pytest
```

To add additional dependencies, for example other CDK libraries, just add to
your requirements.txt file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!


# LlamaAnywhereStack AWS CDK Stack

This stack deploys an EC2 instance in an Amazon VPC along with an S3 bucket. The EC2 instance is configured with the necessary permissions to access the S3 bucket. The instance is also equipped with Docker and Git. The code is cloned from a Github repository and then a container is built and run.

## Prerequisites

- An AWS account with the necessary permissions to create resources.
- AWS CLI installed and configured with the necessary credentials.
- AWS CDK CLI installed.
- Python 3 installed.
- Node.js installed.

## Installation

1. Clone this repository.

```
git clone https://github.com/baileytec-labs/llama-anywhere.git

```


2. Change into the directory for the project.

```
cd llama-anywhere


```


## Usage

The stack takes several parameters that can be supplied using the `cdk.json` file or via the command line using the `--context` option. Below are the parameters:

- `deployType`: This can be either "f" for foundational or "q" for quantized.
- `model`: The model information.
- `hftoken`: Hugging Face token for foundational deployment.
- `instanceType`: The type of EC2 instance to be deployed.
- `region`: The AWS region where the stack is to be deployed.
- `portval`: The port to be opened for HTTP access.

Example:

```bash
cdk deploy --context deployType=f --context model=YourModel --context hftoken=YourToken --context instanceType=t2.micro --context region=us-east-1 --context portval=8080
```

## Outputs

Upon successful deployment, the stack will output:

* BucketName: The name of the S3 bucket.
* InstancePublicIP: The public IP of the EC2 instance.
* DeployType: The deployment type, either "f" for foundational or "q" for quantized.
* InstanceType: The type of the deployed EC2 instance.
* InstancePrice: The on-demand price of the deployed instance type.

The EC2 instance will have Docker and Git installed, and it will clone the repository specified in the user data, build a Docker image, and run a container from the image.

## Clean Up

When you are done using the stack, you can destroy the resources to avoid incurring any further costs.

```
cdk destroy
```

___

# end2endtest.sh/ps1

## Overview

This Bash script automates the process of setting up and deploying a Hugging Face foundational or llama.cpp compatible model, specifically the Llama-2-7B-GGML model, in an AWS cloud environment. It will deploy, test, record, and destroy the environment automatically. The script takes into account the deployment type, the port, instance type, model, and Hugging Face token.

The script also creates a Python virtual environment, installs necessary dependencies, executes AWS CDK deployment commands, and runs a Python script `final_file_upload.py` which can be modified to perform any final tasks after deployment.

## Installation

The script requires Python 3 and AWS CDK to be installed and configured in the environment.

1. Install Python 3: Visit the official Python website and download the appropriate version for your operating system. Follow the installation guide.

2. Install AWS CDK: The AWS Cloud Development Kit (AWS CDK) is an open-source software development framework to define cloud infrastructure in code and provision it through AWS CloudFormation. It enables developers to define their infrastructure in familiar programming languages such as TypeScript, Python, C#, Java etc. Install it by running:


```
npm install -g aws-cdk
```

Please note that AWS CDK requires Node.js. Visit the Node.js website to download and install it, if you haven't already.

## Usage

To run the script, navigate to the directory where the script is stored and provide the necessary arguments:


```
./end2endtest.sh -d <deploy_type> -p <port> -i <instance_type> -m <model_url> -h <huggingface_token>
```

* -d `<deploy_type>`: The type of deployment you want to carry out. The default value is "q".
* -p `<port>`: The port number for your application. The default value is 8080.
* -i `<instance_type>`: The AWS EC2 instance type to use. The default is "t4g.xlarge".
* -m `<model_url>`: The URL of the model to deploy. The default model is "https://huggingface.co/TheBloke/Llama-2-7B-GGML/resolve/main/llama-2-7b.ggmlv3.q2_K.bin".
* -h `<huggingface_token>`: Your Hugging Face token. This is required to authenticate and download the model.


Example:


```
./end2endtest.sh -d q -p 8080 -i t4g.xlarge -m https://huggingface.co/TheBloke/Llama-2-7B-GGML/resolve/main/llama-2-7b.ggmlv3.q2_K.bin -h your_huggingface_token

```

---

# mass_test.py

## Overview

The `mass_test.py` script is designed to test a foundational model from Hugging Face against a quantized model with llama.cpp. It allows for flexibility by allowing testing across multiple instance types and classes. The results of each test will be recorded in `file.log` for analysis.

## Dependencies

You'll need python3.10+ and boto3 installed on your system, as well as the appropriate AWS local configuration:

```
pip3 install boto3 awscli -U
```

## Usage


To run the script, navigate to the directory where the script is stored and provide the necessary arguments:

```

python3 mass_test.py --foundationmodel <foundation_model_path> --quantizedmodel <quantized_model_path> --instancetype <instance_type> --instanceclass <instance_class> --instancecount <instance_count> --hftoken <huggingface_token>

```

* `--foundationmodel`: The path of the foundational model. Default is "VMware/open-llama-7b-v2-open-instruct".
* `--quantizedmodel`: The URL or path of the quantized model. Default is "https://huggingface.co/TheBloke/open-llama-7B-v2-open-instruct-GGML/resolve/main/open-llama-7b-v2-open-instruct.ggmlv3.q2_K.bin".
* `--instancetype`: The type of instance to test against. If multiple instances are selected, provide a comma-separated list. This is optional.
* `--instanceclass`: The class of instance to select from. Options include 'gpu_instances', 'm_instances', 't_instances', 'r_instances', 'c_instances', 'all'. If not specified, a random class is selected.
* `--instancecount`: The number of instances to pull from the instance class. Default is 10.
* ` --hftoken`: Your Hugging Face token. This is required to download private models.

---


# final_file_upload.py

This script is a tool for configuring and interacting with an AWS CloudFormation stack. The tool uses Amazon S3 to upload a file, determines if a given path is a URL, pings a server and configures and invokes it, logs the information, and handles the error traceback.

## Installation
You'll need python3.10 and AWS credentials installed on your local machine for this to work. from there, you can use the included `requirements.txt` file to install all necessary prereqisites:

```
pip3 install -r requirements.txt

```

## Usage

You can run this script with Python 3 from the command line:


```
python final_file_upload.py --stackname my-stack --port 8080 --context 2048 --tokenresponse 512
```

This will run the script with the specified parameters:

* `--stackname`: The name of the stack (default is 'llama-anywhere')
* `--port`: The port to use (default is '8080')
* `--context`: The context (default is 2048)
* `--tokenresponse`: The token response (default is 512)

The script does the following:

1. Initializes a logger that logs to both the console and a file 'file.log'.
2. Defines a class ProgressPercentage for tracking the progress of file upload.
3. Defines several functions, namely get_public_ip for getting the public IP of the stack, is_url for checking if a string is a URL, multipart_upload_with_s3 for uploading a file to Amazon S3, and the main function.
4. The main function does the following:
    * Parses command-line arguments
    * Creates a boto3 session
    * Gets stack details
    * Extracts outputs
    * Logs the public IP, bucket name, selected model, deploy type, instance price, and instance type
    * Depending on the deploy type, prepares the invoke_payload and config_payload, and uploads the model to S3 if necessary
    * Tries to ping the server and logs the response
    * Tries to configure the server and logs the response
    * Tries to invoke the server and logs the response
5. Runs the main function if the script is run as a standalone program.


## Error Handling

The script also handles exceptions by catching them and logging the traceback. If any error occurs while pinging, configuring, or invoking the server, the script logs the error message along with the traceback. The script also retries the ping operation if the server refuses the connection, giving the server time to set up.

Please note that this script relies on Amazon Web Services and therefore requires proper configuration of AWS credentials on the machine where the script is run.





