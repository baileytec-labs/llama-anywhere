#!/bin/bash

deploytype="q"
port="8080"
instancetype="t4g.xlarge"
model="https://huggingface.co/TheBloke/Llama-2-7B-GGML/resolve/main/llama-2-7b.ggmlv3.q2_K.bin"

while getopts ":deploytype:port:instancetype:model:" opt; do
  case $opt in
    deploytype)
      deploytype=$OPTARG
      ;;
    port)
      port=$OPTARG
      ;;
    instancetype)
      instancetype=$OPTARG
      ;;
    model)
      model=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done
echo $model
echo $port
echo $instancetype
echo $deploytype

function cleanup {
    cdk destroy --force
    deactivate
    rm -rf tempvenv
}

trap cleanup EXIT
python3 -m venv tempvenv
source tempvenv/bin/activate 
pip3 install -r requirements.txt
# use variables in context 
cdk deploy --require-approval never -c deployType=$deploytype -c portval=$port -c instanceType=$instancetype -c model=$model

python3 final_file_upload.py
