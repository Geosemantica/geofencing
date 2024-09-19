import aiofiles
from fastapi import UploadFile


async def upload_file(file: UploadFile, path: str, mode='wb'):
    async with aiofiles.open(path, mode) as f:
        await f.write(await file.read())
    await file.close()
