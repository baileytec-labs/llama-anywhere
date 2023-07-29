param(
    [string]$deploytype = "q",
    [string]$port = "8080",
    [string]$instancetype = "t4g.xlarge",
    [string]$model = "https://huggingface.co/TheBloke/Llama-2-7B-GGML/resolve/main/llama-2-7b.ggmlv3.q2_K.bin",
    [string]$huggingface_token = ""
)

Write-Host "Model: $model"
Write-Host "Port: $port"
Write-Host "Instance Type: $instancetype"
Write-Host "Deploy Type: $deploytype"
Write-Host "Huggingface Token: $huggingface_token"

function Cleanup {
    cdk destroy --force
    Deactivate-CondaEnvironment
    Remove-Item -Recurse -Force tempvenv
}

trap { Cleanup; break }

$condaEnv = "tempvenv"

# Create a virtual environment
python -m venv $condaEnv

# Activate the virtual environment
. .\$condaEnv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# use variables in context 
cdk deploy --require-approval never -c deployType=$deploytype -c portval=$port -c instanceType=$instancetype -c model=$model -c hftoken=$huggingface_token

# Call the python script
python final_file_upload.py
