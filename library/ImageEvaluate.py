import aiohttp
import json



class ReqError(Exception):
    pass

class ImageEvaluate(object):
    """图像审查模块"""

    def __init__(self,Subscription:str,region:str) -> None:
        self.Subscription = Subscription
        self.rootUrl = f"https://{region}.api.cognitive.microsoft.com"

    async def getResult(self,ImageURL:str) -> dict:
        """异步请求AzureAPI获取图像审查数据"""
        
        APIurl = f"{self.rootUrl}/contentmoderator/moderate/v1.0/ProcessImage/Evaluate"
        postData = {
            "DataRepresentation":"URL",
            "Value":ImageURL
        }
        header = {
            "Content-Type":"application/json",
            "Ocp-Apim-Subscription-Key": self.Subscription
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(APIurl,headers=header,json=postData) as response:
                    if response.status != 200:
                        raise ReqError         
                    return await response.json()

            except aiohttp.ClientError:
                raise ReqError