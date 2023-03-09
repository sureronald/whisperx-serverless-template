# In this file, we define download_model
# It runs during container build time to get model weights built into the container

# In this example: A Huggingface BERT model

import whisperx
import torch

def download_model():
    device = "cuda"
    model = whisperx.load_model("large", device)

if __name__ == "__main__":
    download_model()
