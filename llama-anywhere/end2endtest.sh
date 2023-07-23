#!/bin/bash

function cleanup {
    cdk destroy --force
}

trap cleanup EXIT

source .venv/bin/activate 
cdk deploy --require-approval never
python3 final_file_upload.py
