import os
import json
import boto3
from fastapi import FastAPI, HTTPException
from starlette.responses import Response
from pydantic import BaseModel, validator
from typing import Optional, List, Union
import traceback
from transformers import AutoModel, AutoTokenizer
#in here we need to instead use huggingface transformers, using a model of the users selection.

MODEL_TYPE=os.environ.get("MODEL_TYPE")
SAVEPATH=os.environ.get("SAVE_PATH")
STAGE = os.environ.get('STAGE', None)
OPENAPI_PREFIX = f"/{STAGE}" if STAGE else "/"

app = FastAPI(title="Sagemaker Endpoint LLM API for HuggingFace Models", openapi_prefix=OPENAPI_PREFIX)

TOKENIZER = AutoTokenizer.from_pretrained(MODEL_TYPE,cache_dir=SAVEPATH)
MODEL = AutoModelForCausalLM.from_pretrained(MODEL_TYPE,cache_dir=SAVEPATH)


class ModelConfig(BaseModel):
    pretrained_model_name: Union[str, Path]
    config_file_name: Optional[Union[str, Path]] = "generation_config.json"
    cache_dir: Optional[Union[str, Path]] = SAVEPATH
    force_download: Optional[bool] = False
    resume_download: Optional[bool] = False
    proxies: Optional[Dict[str, str]] = None
    token: Optional[Union[str, bool]] = None
    revision: Optional[str] = "main"
    return_unused_kwargs: Optional[bool] = False
    subfolder: Optional[str] = ""
    kwargs: Optional[Dict[str, Any]] = None




class ModelArguments(BaseModel):
    input_text: str
    # Length control parameters
    max_length = 20
    max_new_tokens = None
    min_length = 0
    min_new_tokens = None
    early_stopping = False
    max_time = None

    # Generation strategy parameters
    do_sample = False
    num_beams = 1
    num_beam_groups = 1
    penalty_alpha = None
    use_cache = True

    # Logit manipulation parameters
    temperature = 0.7
    top_k = 40
    top_p = 0.95
    typical_p = 1.0
    epsilon_cutoff = 0.0
    eta_cutoff = 0.0
    diversity_penalty = 0.0
    repetition_penalty = 1.1
    encoder_repetition_penalty = 1.1
    length_penalty = 1.0
    no_repeat_ngram_size = 0
    bad_words_ids = None
    force_words_ids = None
    renormalize_logits = False
    constraints = None
    forced_bos_token_id = None
    forced_eos_token_id = None
    remove_invalid_values = None
    exponential_decay_length_penalty = None
    suppress_tokens = None
    begin_suppress_tokens = None
    forced_decoder_ids = None
    sequence_bias = None
    guidance_scale = None

    # Output variables parameters
    num_return_sequences = 1
    output_attentions = False
    output_hidden_states = False
    output_scores = False
    return_dict_in_generate = False

    # Special tokens parameters
    pad_token_id = None
    bos_token_id = None
    eos_token_id = None

    # Encoder-decoder exclusive parameters
    encoder_no_repeat_ngram_size = 0
    decoder_start_token_id = None


    @validator('tensor_split')
    def validate_tensor_split(cls, v):
        if v is not None and not all(isinstance(item, float) for item in v):
            raise ValueError('All elements in the tensor_split list must be floats')
        return v

class RoutePayload(BaseModel):
    configure: bool
    inference: bool
    args: dict

def download_from_s3(bucket: str, key: str, local_path: str):
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, local_path)

@app.post("/")
async def route(payload: RoutePayload):
    if payload.configure:
        llama_model_args = LlamaModelConfig(**payload.args)
        return await configure(llama_model_args)
    elif payload.inference:
        model_args = LlamaArguments(**payload.args)
        return await invoke(model_args)
    else:
        raise HTTPException(status_code=400, detail="Please specify either 'configure' or 'inference'")



@app.get("/ping")
async def ping():
    return Response(status_code=200)


@app.post("/invoke")
async def invoke(model_args: ModelArguments):
    try:
        model_args=model_args.dict()
        input_text=model_args.pop("input_text",None)
        inputs=TOKENIZER.encode(input_text,return_tensors="pt")
        outputs=MODEL.generate(inputs,**model_args)
        finaloutdata={}
        for i, outdata in enumerate(outputs):
            print(f"{i}: {tokenizer.decode(output)}")
            finaloutdata{i}=tokenizer.decode(output)
        output=finaloutdata

    except:
        output={"traceback_err":str(traceback.format_exc())}
    return output

@app.post("/configure")
async def configure(model_config_args: ModelConfig):
    try:
        global TOKENIZER
        global MODEL
        TOKENIZER = AutoTokenizer.from_pretrained(**model_config_args.dict())
        MODEL = AutoTokenizer.from_pretrained(**model_config_args.dict())
        
        return {"status": "success"}
    except:
        return {"traceback_err":str(traceback.format_exc())}

