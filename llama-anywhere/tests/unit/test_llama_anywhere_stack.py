import aws_cdk as core
import aws_cdk.assertions as assertions
from llama_anywhere.llama_anywhere_stack import LlamaAnywhereStack


def test_s3_bucket_created():
    app = core.App()
    stack = LlamaAnywhereStack(app, "llama-anywhere")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::S3::Bucket", 1)


def test_vpc_created():
    app = core.App()
    stack = LlamaAnywhereStack(app, "llama-anywhere")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::VPC", 1)


def test_iam_role_created():
    app = core.App()
    stack = LlamaAnywhereStack(app, "llama-anywhere")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::IAM::Role", 1)


def test_ec2_instance_created():
    app = core.App()
    stack = LlamaAnywhereStack(app, "llama-anywhere")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::Instance", 1)


def test_security_group_created():
    app = core.App()
    stack = LlamaAnywhereStack(app, "llama-anywhere")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::SecurityGroup", 1)


def test_bucket_name_output():
    app = core.App()
    stack = LlamaAnywhereStack(app, "llama-anywhere")
    template = assertions.Template.from_stack(stack)

    template.has_output("BucketName", {})


def test_instance_public_ip_output():
    app = core.App()
    stack = LlamaAnywhereStack(app, "llama-anywhere")
    template = assertions.Template.from_stack(stack)

    template.has_output("InstancePublicIP", {})
