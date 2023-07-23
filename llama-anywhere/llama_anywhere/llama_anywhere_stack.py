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
import time
import requests


# get public IP
my_public_ip = requests.get('https://api.ipify.org').text


LOCALMODEL="/Users/seanbailey/Github/llama-anywhere/llama2-testmodel.bin"

class LlamaAnywhereStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
            connection=ec2.Port.tcp(80),
            description="Allow HTTP access from current public IP"
        )

        # Define the user data to install Docker, git and other dependencies
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "yum install docker -y",
            "usermod -a -G docker ec2-user",
            "yum install git -y",
            "service docker start",
            "chkconfig docker on",
            "cd /home/ec2-user",
            "su - ec2-user -c 'cd /home/ec2-user && git clone https://github.com/baileytec-labs/llama-anywhere.git'", 
            "cd llama-anywhere && cd sagemaker_container && DOCKER_BUILDKIT=1 docker build -t my-container . && docker run -p 80:80 -d my-container",
        )

        # Define a new EC2 instance
        instance = ec2.CfnInstance(
            self, "Instance",
            instance_type="t4g.xlarge",
            image_id=ec2.MachineImage.latest_amazon_linux2(cpu_type=ec2.AmazonLinuxCpuType.ARM_64).get_image(self).image_id,
            subnet_id=vpc.public_subnets[0].subnet_id,
            iam_instance_profile=instance_profile.ref,
            security_group_ids=[sg.security_group_id],
            user_data=cdk.Fn.base64(user_data.render()),
            key_name="shabadedoo",  # replace this with the name of your key pair
            block_device_mappings=[  # attach a 50 GB EBS volume
                {
                    "deviceName": "/dev/sda1",  # this can be different depending on your AMI
                    "ebs": {
                        "volumeSize": 50,  # specify the volume size in GB
                        "deleteOnTermination": True,  # delete the volume when the instance is terminated
                        "volumeType": "gp3"  # specify the volume type. gp2 is general purpose SSD volume type
                    }
                }
            ]
        )

        # Use boto3 to upload a file to the newly created bucket
        #s3_client = boto3.client('s3')

        #with open(LOCALMODEL, 'rb') as data:
        #    s3_client.upload_fileobj(data, bucket_name, LOCALMODEL.split("/")[-1])


        cdk.CfnOutput(self, "ObjectName",value=LOCALMODEL.split("/")[-1])
        cdk.CfnOutput(self, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(self, "InstancePublicIP", value=instance.attr_public_ip)
