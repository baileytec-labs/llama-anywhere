from transformers import AutoModel, AutoTokenizer, pipeline
import os
import traceback




try:

    SAVEPATH=os.environ.get("SAVE_PATH")
    MODEL = os.environ.get("MODEL_TYPE")

    print(SAVEPATH)
    print(MODEL)

    #pipe=pipeline(task="text-generation",model=MODEL, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL,cache_dir=SAVEPATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL,cache_dir=SAVEPATH)
    #I'm hoping that this will download to the appropriate local directory and it will check there first. Who knows?
except:
    print(traceback.format_exc())