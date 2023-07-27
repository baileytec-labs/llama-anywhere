import os
import json
import boto3
from fastapi import FastAPI, HTTPException
from starlette.responses import Response
from pydantic import BaseModel, validator
from typing import Optional, List, Union
from typing import Dict, Optional
from typing import Union, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel
import traceback
from typing import ClassVar
from pydantic import BaseModel
from pathlib import Path
from transformers import AutoModel, AutoTokenizer
from typing import Optional, List, ClassVar
from pydantic import BaseModel, validator
#in here we need to instead use huggingface transformers, using a model of the users selection.

MODEL_TYPE=os.environ.get("MODEL_TYPE")
SAVEPATH=os.environ.get("SAVE_PATH")
STAGE = os.environ.get('STAGE', None)
OPENAPI_PREFIX = f"/{STAGE}" if STAGE else "/"


app = FastAPI(title="Sagemaker Endpoint LLM API for HuggingFace Models", openapi_prefix=OPENAPI_PREFIX)

TOKENIZER = AutoTokenizer.from_pretrained(MODEL_TYPE,cache_dir=SAVEPATH)
MODEL = AutoModel.from_pretrained(MODEL_TYPE,cache_dir=SAVEPATH)

print(MODEL_TYPE)
print(SAVEPATH)

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
    max_length: ClassVar[int] = 20
    max_new_tokens: Optional[int] = None
    min_length: int = 0
    min_new_tokens: Optional[int] = None
    early_stopping: bool = False
    max_time: Optional[float] = None

    # Generation strategy parameters
    do_sample: bool = False
    num_beams: int = 1
    num_beam_groups: int = 1
    penalty_alpha: Optional[float] = None
    use_cache: bool = True

    # Logit manipulation parameters
    temperature: float = 0.7
    top_k: int = 40
    top_p: float = 0.95
    typical_p: float = 1.0
    epsilon_cutoff: float = 0.0
    eta_cutoff: float = 0.0
    diversity_penalty: float = 0.0
    repetition_penalty: float = 1.1
    encoder_repetition_penalty: float = 1.1
    length_penalty: float = 1.0
    no_repeat_ngram_size: int = 0
    bad_words_ids: Optional[List[int]] = None
    force_words_ids: Optional[List[int]] = None
    renormalize_logits: bool = False
    constraints: Optional[str] = None
    forced_bos_token_id: Optional[int] = None
    forced_eos_token_id: Optional[int] = None
    remove_invalid_values: Optional[bool] = None
    exponential_decay_length_penalty: Optional[bool] = None
    suppress_tokens: Optional[List[int]] = None
    begin_suppress_tokens: Optional[List[int]] = None
    forced_decoder_ids: Optional[List[int]] = None
    sequence_bias: Optional[float] = None
    guidance_scale: Optional[float] = None

    # Output variables parameters
    num_return_sequences: int = 1
    output_attentions: bool = False
    output_hidden_states: bool = False
    output_scores: bool = False
    return_dict_in_generate: bool = False

    # Special tokens parameters
    pad_token_id: Optional[int] = None
    bos_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None

    # Encoder-decoder exclusive parameters
    encoder_no_repeat_ngram_size: int = 0
    decoder_start_token_id: Optional[int] = None

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
        llama_model_args = ModelConfig(**payload.args)
        return await configure(llama_model_args)
    elif payload.inference:
        model_args = ModelArguments(**payload.args)
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
            print(f"{i}: {TOKENIZER.decode(output)}")
            finaloutdata[i]=TOKENIZER.decode(output)
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
        MODEL = AutoModel.from_pretrained(**model_config_args.dict())
        
        return {"status": "success"}
    except:
        return {"traceback_err":str(traceback.format_exc())}

