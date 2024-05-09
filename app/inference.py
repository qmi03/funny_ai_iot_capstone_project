import asyncio

from aiohttp import ClientSession

headers = {"Authorization": f"Bearer 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"}
API_URL = "https://api-inference.huggingface.co/models/vinai/PhoWhisper-base"


async def query(filename):
    async with ClientSession() as session:
        with open(filename, "rb") as f:
            data = f.read()
        async with session.post(API_URL, headers=headers, data=data) as response:
            return await response.json()


async def main():
    output = await query("uploads/audio.flac")
    print(output)


if __name__ == "__main__":
    asyncio.run(main())
