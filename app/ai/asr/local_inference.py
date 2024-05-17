import asyncio
import warnings

import torch
from transformers import pipeline

warnings.filterwarnings("ignore", category=FutureWarning)
device = ""
if torch.cuda.is_available():
    device = "cuda:0"
else:
    try:
        if torch.backends.mps.is_available():
            device = "mps:0"
    except:
        device = "cpu"

model_id = "vinai/PhoWhisper-base"

transcriber = pipeline(
    "automatic-speech-recognition", model="vinai/PhoWhisper-base", device=device
)


async def query(filename):
    try:
        output = transcriber(filename)
        return output
    except Exception as e:
        return {"error": f"Error processing audio: {str(e)}"}


async def main():
    output = await query("uploads/audio.flac")
    print(output)


if __name__ == "__main__":
    asyncio.run(main())
