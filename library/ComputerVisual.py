import aiohttp
import aiocache
from pydantic import BaseModel, Field
from typing import Literal



class ReqError(Exception):
    """请求异常"""
    def __str__(self):
        return repr("请求非200应答  请检查是否输入正确的密钥和终结点（或区域）")

class ObjectInitError(Exception):
    """区域和终结点不可共存"""

    def __str__(self):
        return repr("区域和终结点不可共存，您只能填写其中一个参数用于请求")






class ApiConfig(object):
    """API设置"""

    Subscription:str = ""
    region:str = ""
    endpoint:str = ""
    header:dict = {}
    rootUrl:str = ""

    def __init__(
        self,
        Subscription:str,
        region:str="",
        endpoint:str="") -> None:

        if endpoint and region:
            """区域和终结点不可共存"""
            raise ObjectInitError
            
        self.header = {
                "Content-Type":"application/json",
                "Ocp-Apim-Subscription-Key": Subscription
        }
        
        self.rootUrl = f"https://{region}.api.cognitive.microsoft.com"
        if endpoint:
            self.rootUrl = endpoint


class Modles(object):
    """各种返回基类"""
    class ImageExamination(BaseModel):
        """图像审查返回基类"""
        class _AdvInfo(BaseModel):
            Key:str
            Value:str

        class _st(BaseModel):
            Code:int
            Description:str
            exception = Field(..., alias="Exception")
        
        AdultClassificationScore:float
        IsImageAdultClassified:bool
        #是否为成人内容
        RacyClassificationScore:float
        IsImageRacyClassified:bool
        #是否性暗示内容或成人内容
        Result:bool
        #最终判定
        AdvancedInfo:list[_AdvInfo]
        Status:_st
        #状态
        TrackingId:str
        #请求追踪id

    class ComputerVisual(BaseModel):
        """机器视觉返回基类"""
        class _categorie (BaseModel):
            name:str
            score:float

        categories:list[_categorie] #标签列表
        requestId:str #请求id
        class _met(BaseModel):
            """图像元数据"""
            height:int
            width:int
            format:str
        modelVersion:str
        metadata:_met







class ComputerVisual(object):
    """异步机器视觉模块"""
       
    class ImageExamination:
        """图像审查模块"""
        def __init__(self, config:ApiConfig) -> None:
            self.config = config


        @aiocache.cached(ttl=600)#或许是一个必要的缓存，避免Azureapi请求数超额
        async def request(self,ImageURL:str) -> Modles.ImageExamination:
            """异步请求AzureAPI获取图像审查数据"""
            
            APIurl = f"{self.config.rootUrl}/contentmoderator/moderate/v1.0/ProcessImage/Evaluate"
            postData = {
                "DataRepresentation":"URL",
                "Value":ImageURL
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(APIurl,headers=self.config.header,json=postData) as response:
                        if response.status != 200:
                            raise ReqError
                        return  Modles.ImageExamination.parse_obj(await response.json())

                except aiohttp.ClientError:
                    raise ReqError


    class ComputerVisual(object):
        """图像认知模块"""

        def __init__(self, config:ApiConfig) -> None:
            self.config = config


        @aiocache.cached(ttl=600)#或许是一个必要的缓存，避免Azureapi请求数超额
        async def request(
            self,
            ImageURL:str,
            language:Literal[
                'ar', 'az', 'bg', 'bs',
                "ca", "cs", "cy", "da",
                "de", "el", "en", "es",
                "et", "eu", "fi", "fr",
                "ga", "gl", "he", "hi",
                "hr", "hu", "id", "it",
                "ja", "kk", "ko", "lt",
                "lv", "mk", "ms", "nb",
                "nl","pl","prs","pt",
                "pt-BR","pt-PT","ro",
                "ru","sk","sl","sl-Cyrl",
                "sl-Latn","sv","th","tr","uk","vi","zh"
                ]="zh"
                ) -> Modles.ComputerVisual:

            """异步请求AzureAPI获取图像审查数据"""
            
            APIurl = f"{self.config.rootUrl}/vision/v3.2/analyze"
            postData = {"url":ImageURL}
            param = {
                "visualFeatures":"Categories",
                "language":language
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        APIurl,
                        headers=self.config.header,
                        json=postData,
                        params=param) as response:

                        if response.status != 200:
                            raise ReqError
                        return Modles.ComputerVisual.parse_obj(await response.json())

                except aiohttp.ClientError:
                    raise ReqError
