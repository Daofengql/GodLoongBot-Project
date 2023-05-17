import mimetypes
import os
import json
from b2sdk.v1 import B2Api
from pathlib import Path

# 创建 B2Api 对象
b2_api = B2Api()


PATH = Path(os.getcwd())

if not os.path.exists(PATH / "b2access.json"):
    js = {
        "key_id": "",
        "key":"",
        "bucket": ""
        }
    with open(PATH / "b2access.json","w") as f:
        js = json.dumps(js)
        f.write(js)
else:
    with open(PATH / "b2access.json","r") as f:
        conf = json.loads(f.read())
        
        
# 鉴权
application_key_id = conf["key_id"]
application_key = conf["key"]
bucket_name = conf["bucket"]

b2_api.authorize_account("production", application_key_id, application_key)
bucket = b2_api.get_bucket_by_name(bucket_name)

# 根据文件后缀名猜测 Content-Type
async def guess_content_type(file_name:str):
    if file_name.split(".")[-1].lower() == "webp":
        return "image/webp"
    
    
    content_type, _ = mimetypes.guess_type(file_name)
    if not content_type:
        return "binary/octet-stream"
    return content_type

