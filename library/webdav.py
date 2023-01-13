from webdav3.client import Client
from library.ToThread import run_withaio

import json,os
from pathlib import Path
from io import BytesIO



PATH = Path(os.getcwd())

if not os.path.exists(PATH / "webdavConf.json"):
    js = {
        'webdav_hostname': "",
        'webdav_login': "",
        'webdav_password': "",
        'disable_check': True

    }
    with open(PATH / "webdavConf.json","w") as f:
        js = json.dumps(js)
        f.write(js)
else:
    with open(PATH / "webdavConf.json","r") as f:
        options = json.loads(f.read())



async def uploadToAlist(upnane,filepath):

    client = Client(options)
    try:
        await run_withaio(client.upload,args=(upnane,filepath,))
    except:
        return False
    else:
        return True

async def downloadFromAlist(filepath):

    client = Client(options)
    ret = BytesIO()

    try:
        it = await run_withaio(client.download_iter,args=(filepath,))
    except:
        return False
    
    
    for t in it:
        ret.write(t)

    ret.seek(0)
    return ret.read()

async def deleteFromAlist(filepath):
    client = Client(options)
    try:
        await run_withaio(client.clean,args=(filepath,))
    except:
        return False
    else:
        return True

async def listDictFromAlist(filepath):
    client = Client(options)
    try:
        await run_withaio(client.list,args=(filepath,))
    except:
        return False
    else:
        return True

async def moveFromAlist(origin,target):
    client = Client(options)
    try:
        await run_withaio(client.move,args=(origin,target,))
    except:
        return False
    else:
        return True

