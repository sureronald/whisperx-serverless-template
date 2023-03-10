import torch
import whisperx
import os
import base64
from io import BytesIO

DEVICE = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
# Init is ran on server startup
# Load your model to GPU as a global variable here using the variable name "model"
def init():
    global model
    model = whisperx.load_model("large", DEVICE)
    print(f"CUDA available? {torch.cuda.is_available()}, device: {DEVICE}")

def extract_segments(segments_list):
    resp = []
    for seg in segments_list:
        resp.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': seg['text']
        })
    return resp

# Inference is ran for every server call
# Reference your preloaded global model variable here.
def inference(model_inputs:dict) -> dict:
    global model
    # Parse out your arguments
    language = model_inputs.get("language", None)
    mp3BytesString = model_inputs.get('mp3BytesString', None)
    if mp3BytesString == None:
        return {'message': "No input provided"}
    
    mp3Bytes = BytesIO(base64.b64decode(mp3BytesString.encode("ISO-8859-1")))
    audio_file_name = "input.mp3"
    with open(audio_file_name,'wb') as file:
        file.write(mp3Bytes.getbuffer())
    
    # Run the model
    result = model.transcribe(audio_file_name, language=language)

    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_file_name, DEVICE)
    os.remove(audio_file_name)
    response = {
        'word_segments': result_aligned["word_segments"],
        'paragraphs': extract_segments(result_aligned['segments'])
    }
    return response

