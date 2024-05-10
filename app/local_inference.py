import torch
from transformers import pipeline
import asyncio

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model_id = "vinai/PhoWhisper-base"

transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-base",device=device)
async def query(filename):
    return transcriber(filename)

async def main():
    output = await query("uploads/audio.flac")
    print(output)

if __name__ == "__main__":
    asyncio.run(main())
