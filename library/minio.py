import mimetypes
import os
import json
import minio
from b2sdk.v1 import B2Api
from pathlib import Path

# 创建 B2Api 对象
b2_api = B2Api()


PATH = Path(os.getcwd())

if not os.path.exists(PATH / "minio.json"):
    minio_conf = {
    "conf":{
        'endpoint': '0.0.0.0:9000',
    'access_key': 'admin',
    'secret_key': '123456',
    'secure': False,
    },
    "bucket":"godloongbot"
    }

    with open(PATH / "minio.json","w") as f:
        minio_conf = json.dumps(minio_conf)
        f.write(minio_conf)
else:
    with open(PATH / "minio.json","r") as f:
        minio_conf = json.loads(f.read())

client = minio.Minio(**minio_conf["conf"])

# 根据文件后缀名猜测 Content-Type
async def guess_content_type(file_name:str):
    if file_name.split(".")[-1].lower() == "webp":
        return "image/webp"
    
    
    content_type, _ = mimetypes.guess_type(file_name)
    if not content_type:
        return "binary/octet-stream"
    return content_type

