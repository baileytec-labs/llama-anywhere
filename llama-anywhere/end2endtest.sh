#!/bin/bash

deploytype=""
port=""
instancetype=""
model=""

while getopts ":deploytype:port:instancetype:model:" opt; do
  case $opt in
    deploytype)
      echo "-deploytype was triggered, Parameter: $OPTARG" >&2
      deploytype=$OPTARG
      ;;
    port)
      echo "-port was triggered, Parameter: $OPTARG" >&2
      port=$OPTARG
      ;;
    instancetype)
      echo "-instancetype was triggered, Parameter: $OPTARG" >&2
      instancetype=$OPTARG
      ;;
    model)
      echo "-model was triggered, Parameter: $OPTARG" >&2
      model=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

function cleanup {
    cdk destroy --force
}

trap cleanup EXIT

source .venv/bin/activate 

# use variables in context 
cdk deploy --require-approval never -c deployType=$deploytype -c port=$port -c instanceType=$instancetype -c model=$model

python3 final_file_upload.py
