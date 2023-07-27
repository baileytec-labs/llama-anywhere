from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_s3 as s3,
)
import aws_cdk as cdk
import boto3
import uuid
import requests
import json


# get public IP
my_public_ip = requests.get('https://api.ipify.org').text
#portval=8080


gpu_instances=['g4ad', 'g4dn', 'g5', 'inf1', 'p2', 'p3', 'p3dn', 'p4d', 'p4de', 'p4ov', 'v100']


#based on the instance type that is selected, we can also have the on-demand price written to cloudformation variables, and process it downstream.
def get_on_demand_price(instance_type, region_name):
    pricing = boto3.client('pricing', region_name='us-east-1')

    response = pricing.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': region_name},
            {'Type': 'TERM_MATCH', 'Field': 'termType', 'Value': 'OnDemand'}
        ],
        MaxResults=100
    )

    for product in response['PriceList']:
        product_obj = json.loads(product)
        product_terms = product_obj['terms']

        for term in product_terms.values():
            for term_price_details in term.values():
                price_dimensions = term_price_details['priceDimensions']

                for price_dimension in price_dimensions.values():
                    if price_dimension['unit'] == 'Hrs':
                        return float(price_dimension['pricePerUnit']['USD'])
                    
    return None

def get_latest_deep_learning_ami(region_name='us-east-1'):
    ec2_client = boto3.client('ec2', region_name=region_name)
    
    response = ec2_client.describe_images(
        Owners=['amazon'],
        Filters=[
            {'Name': 'name', 'Values': ['Deep Learning AMI GPU PyTorch * (Amazon Linux 2) *']},
            #{'Name': 'state', 'Values': ['available']},
            #{'Name': 'description', 'Values': ['Deep Learning AMI with NVIDIA CUDA 11 Driver, Intel MKL-DNN, Docker, NVIDIA Docker, AWS Neuron, NVIDIA Deep Learning Containers (optimized for PyTorch)*']}
        ]
    )
    
    # Sort images by creation date
    images = sorted(response['Images'], key=lambda k: k['CreationDate'], reverse=True)
    #print(images)

    # Return the latest image id
    return images[0]['ImageId'] if images else None


def determine_architecture(instance_type):
    if instance_type is not None:
        ec2client = boto3.client('ec2', region_name='us-east-1')
        response = ec2client.describe_instance_types(InstanceTypes=[instance_type])
        #should return a list of architectures. I only care about 'x86_64' or 'arm64'
        architectures = response['InstanceTypes'][0]['ProcessorInfo']['SupportedArchitectures']

        if 'arm64' in architectures:
            return ec2.AmazonLinuxCpuType.ARM_64
        elif 'x86_64' in architectures:
            return ec2.AmazonLinuxCpuType.X86_64
    else:
        return None
    #print(response['InstanceTypes'][0]['ProcessorInfo']['SupportedArchitectures'])



class LlamaAnywhereStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #we want to have a single standardized stack. You will deploy either a quantized model or a foundational model.
        #Keep all downstream variables and outputs the same. Add in some form of notation whether you chose quantized or foundational
        #Let's modify the functionality a little bit, so that the model can be specified either locally or via a url, and it 
        #takes care of things that way.

        #SavePath doesn't matter. We don't need to specify it, we can hardcode that in the Docker container without penalty.

        #We should ideally just specify if this is a quantized or foundational deployment...
        DEPLOYTYPE= self.node.try_get_context("deployType")
        #make it so we're looking for "q" or "f". Actually, funny enough, those letters are unique to each word so I'll be a bit cheeky.

        #We will need some form of model info which will be universally consumed and processed based on the endpoint type...

        MODEL = self.node.try_get_context("model")

        #LOCALMODEL = self.node.try_get_context('localModel')
        #key_name = self.node.try_get_context('keyName')
        
        #We'll need to specify some form of instance type based on the deployment.
        instance_type = self.node.try_get_context('instanceType')
        regionval=self.node.try_get_context('region')
        if regionval is None:
            regionval="us-east-1"

        #We'll want to specify some form of port based on the deployment.
        #I have to wrap this in a try-except when using cdk destroy.
        try:
            portval=int(self.node.try_get_context("portval"))
        except:
            portval=8080
        
        
        #HFMODEL = self.node.try_get_context('hfModel')
        #SAVEPATH = self.node.try_get_context('savePath')


        bucket_name="llama-anywhere"+str(uuid.uuid4()).replace("-","").replace("_","")
        # Define a new S3 Bucket
        bucket = s3.Bucket(self, "MyBucket",bucket_name=bucket_name)

        vpc = ec2.Vpc(self, "MyVPC", max_azs=2)

        # Define a new IAM Role with S3 full access policy
        role = iam.Role(self, "MyRole",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        bucket.grant_read_write(role)

        instance_profile = iam.CfnInstanceProfile(self, "InstanceProfile",
                                                  roles=[role.role_name])

        # Define a new security group
        sg = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=vpc
        )

        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(my_public_ip + "/32"),  # /32 means a single IP
            connection=ec2.Port.tcp(22),
            description="Allow SSH access from current public IP"
        )

        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(my_public_ip + "/32"),  # /32 means a single IP
            connection=ec2.Port.tcp(portval),
            description="Allow HTTP access from current public IP"
        )
        
        IMAGEID=None
        GPUINSTANCE=False
        #This will give us the ability to automatically get an EC2 instance with the appropriate drivers and gpu availability installed. 
        architecture = determine_architecture(instance_type)
        if instance_type is not None:
            instanceclass=instance_type.split('.')[0]
            if instanceclass in gpu_instances:
                IMAGEID=get_latest_deep_learning_ami(regionval)
                GPUINSTANCE=True
            else:
                IMAGEID=ec2.MachineImage.latest_amazon_linux2(cpu_type=architecture).get_image(self).image_id
        userdataline=""
        downloadline=""
        if DEPLOYTYPE is not None:
            if 'Q' in DEPLOYTYPE.upper():
                if GPUINSTANCE:
                    downloadline = """sudo su - ec2-user -c "bash -c 'cd /home/ec2-user; git clone https://github.com/baileytec-labs/llama-anywhere.git'" > /home/ec2-user/userdata.log 2>&1"""
                    userdataline="""sudo su - ec2-user -c 'cd /home/ec2-user/llama-anywhere/quantized_container && DOCKER_BUILDKIT=1 docker build -t my-container . && docker run --gpus all -p {portval}:{portval} -d my-container'"""

                else:
                    downloadline="su - ec2-user -c 'cd /home/ec2-user && git clone https://github.com/baileytec-labs/llama-anywhere.git'"
                    userdataline="cd llama-anywhere && cd quantized_container && DOCKER_BUILDKIT=1 docker build -t my-container . && docker run -p "+str(portval)+":"+str(portval)+" -d my-container"
            if 'F' in DEPLOYTYPE.upper():
                if GPUINSTANCE:
                    downloadline = """sudo su - ec2-user -c "bash -c 'cd /home/ec2-user; git clone https://github.com/baileytec-labs/llama-anywhere.git'" > /home/ec2-user/userdata.log 2>&1"""
                    userdataline="sudo su - ec2-user -c 'cd /home/ec2-user/llama-anywhere/foundational_container && DOCKER_BUILDKIT=1 docker build --build-arg MODEL="+MODEL+" -t my-container . && docker run --gpus all -p "+str(portval)+":"+str(portval)+" -d my-container'"
                else:
                    downloadline="su - ec2-user -c 'cd /home/ec2-user && git clone https://github.com/baileytec-labs/llama-anywhere.git'"
                    userdataline="cd llama-anywhere && cd foundational_container && DOCKER_BUILDKIT=1 docker build --build-arg MODEL="+MODEL+" -t my-container . && docker run -p "+str(portval)+":"+str(portval)+" -d my-container"

            # Define the user data to install Docker, git and other dependencies
        print(downloadline),
        print(userdataline)
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "yum install docker -y",
            "usermod -a -G docker ec2-user",
            "yum install git -y",
            "service docker start",
            "chkconfig docker on",
            "cd /home/ec2-user",
            downloadline, 
            userdataline,
        )
        

        # Define a new EC2 instance for testing the  model
        instance = ec2.CfnInstance(
            self, "Instance",
            instance_type=instance_type,
            #here is a bit of a pickle. I need to have this determine automatically if this is going to be an x86 or arm processor and select an image id.
            #We could also have the user specify it as well...
            image_id=IMAGEID,
            subnet_id=vpc.public_subnets[0].subnet_id,
            iam_instance_profile=instance_profile.ref,
            security_group_ids=[sg.security_group_id],
            user_data=cdk.Fn.base64(user_data.render()),
            key_name="shabadedoo",  # replace this with the name of your key pair
            block_device_mappings=[  # attach a 200 GB EBS volume
                {
                    "deviceName": "/dev/xvda",  # this can be different depending on your AMI
                    "ebs": {
                        "volumeSize": 200,  # specify the volume size in GB
                        "deleteOnTermination": True,  # delete the volume when the instance is terminated
                        "volumeType": "gp3"  # specify the volume type. gp3 is general purpose SSD volume type
                    }
                }
            ]
        )



        #Down the line we will process if its huggingface / a url / local
        if MODEL is not None:
            cdk.CfnOutput(self, "ObjectName",value=MODEL)
        
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "InstancePublicIP", value=instance.attr_public_ip)
        if DEPLOYTYPE is not None:
            cdk.CfnOutput(self,"DeployType",value=DEPLOYTYPE)
        if instance_type is not None:
            cdk.CfnOutput(self,"InstanceType",value=instance_type)
            #gonna hardcode virginia here because the pricing sdk is limited, so I would prefer it working.
            cdk.CfnOutput(self,"InstancePrice",value=str(get_on_demand_price(instance_type,'US East (N. Virginia)')))
