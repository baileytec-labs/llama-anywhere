#!/usr/bin/env python3

import aws_cdk as cdk

from llama_anywhere.llama_anywhere_stack import LlamaAnywhereStack


app = cdk.App()
LlamaAnywhereStack(app, "llama-anywhere")

app.synth()
