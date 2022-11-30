import aiohttp
import aiocache
import asyncio
from pydantic import BaseModel, Field
from typing import Literal,Any
import random
import azure.cognitiveservices.speech as speechsdk


class ReqError(Exception):
    """请求异常"""
    def __str__(self):
        return repr("请求非200应答  请检查是否输入正确的密钥和终结点（或区域）")

class ObjectInitError(Exception):
    """区域和终结点不可共存"""

    def __str__(self):
        return repr("区域和终结点不可共存，您只能填写其中一个参数用于请求")

class RequestTooFast(Exception):
    """您的请求过快"""

    def __str__(self):
        return repr("您的请求过快")






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
            error:Any = Field(..., alias="Exception")
        
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

    class ComputerVisual(object):
        """机器视觉返回基类"""

        class AnalyzeImage(BaseModel):
            """图像分析返回基类"""
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
        
        class DescribeImage(BaseModel):
            """图像分析返回基类"""
            class _description(BaseModel):

                class _captions(BaseModel):
                    text:str
                    confidence:float
                    
                tags:list[str]
                captions:list[_captions]

            description:_description
            requestId:str

            class _met(BaseModel):
                """图像元数据"""
                height:int
                width:int
                format:str
            modelVersion:str
            metadata:_met

        class TagImage(BaseModel):
            """图像分析返回基类"""

            class _tag(BaseModel):
                name:str
                confidence:float
                    
            tags:list[_tag]


            requestId:str

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
                        if response.status == 429:
                            raise RequestTooFast
                        elif response.status != 200:
                            raise ReqError
                        return  Modles.ImageExamination.parse_obj(await response.json())

                except aiohttp.ClientError:
                    raise ReqError


    class ComputerVisual(object):
        """图像认知模块"""

        def __init__(self, config:ApiConfig) -> None:
            self.config = config
            self.config.rootUrl = self.config.rootUrl + "/vision/v3.2/"

        @aiocache.cached(ttl=600)#或许是一个必要的缓存，避免Azureapi请求数超额
        async def _requests(
            self,
            func:str = "",
            ImageURL:str="",
            ImageBin:bytes=b"",
            param = {}
            ) -> dict:


            APIurl = f"{self.config.rootUrl}{func}"

            async with aiohttp.ClientSession() as session:
                try:
                    if ImageBin:
                        async with session.post(
                            APIurl,
                            headers=self.config.header,
                            data=ImageBin,
                            params=param) as response:
                            if response.status == 429:
                                raise RequestTooFast
                            elif response.status != 200:
                                raise ReqError
                            return await response.json()
                            
                    else:
                        postData = {"url":ImageURL}
                        async with session.post(
                            APIurl,
                            headers=self.config.header,
                            json=postData,
                            params=param) as response:

                            if response.status == 429:
                                raise RequestTooFast
                            elif response.status != 200:
                                raise ReqError
                            return await response.json()

                except aiohttp.ClientError:
                    raise ReqError
            


        async def AnalyzeImage(
            self,
            ImageURL:str="",
            ImageBin:bytes=b"",
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
                ) -> Modles.ComputerVisual.AnalyzeImage:

            """异步请求AzureAPI获取图像审查数据"""

            param = {
                "visualFeatures":"Categories",
                "language":language
            }

            data = await self._requests(
                ImageBin=ImageBin,
                ImageURL=ImageURL,
                func="analyze",
                param=param
            )
            return Modles.ComputerVisual.AnalyzeImage.parse_obj(data)


        async def DescribeImage(
            self,
            ImageURL:str="",
            ImageBin:bytes=b"",
            language:Literal[
                'en', 'es', 'ja', 'pt',"zh"
                ]="zh",
            maxCandidates:int = 1
            ) -> Modles.ComputerVisual.DescribeImage:

            """异步请求AzureAPI获取图像审查数据"""
            param = {
                "maxCandidates":maxCandidates,
                "language":language
            }
       
            data = await self._requests(
                ImageBin=ImageBin,
                ImageURL=ImageURL,
                func="describe",
                param=param
            )
            return Modles.ComputerVisual.DescribeImage.parse_obj(data)
        
        async def TagImage(
            self,
            ImageURL:str="",
            ImageBin:bytes=b"",
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
                ) -> Modles.ComputerVisual.TagImage:

            """异步请求AzureAPI获取图像审查数据"""

            param = {
                "visualFeatures":"Categories",
                "language":language
            }

            data = await self._requests(
                ImageBin=ImageBin,
                ImageURL=ImageURL,
                func="tag",
                param=param
            )

            return Modles.ComputerVisual.TagImage.parse_obj(data)


class Speech:
    """图像审查模块"""
    def __init__(self, Subscription,region) -> None:
        self.Subscription = Subscription
        self.region = region

        self.STYLELIST = [
            "advertisement_upbeat","affectionate",
            "angry","assistant",
            "calm","chat",
            "cheerful","customerservice",
            "depressed","disgruntled",
            "documentary-narration","embarrassed",
            "empathetic","envious",
            "excited","fearful","friendly",
            "gentle","hopeful","lyrical",
            "narration-professional","narration-relaxed",
            "newscast","newscast-casual",
            "newscast-formal","poetry-reading",
            "sad","serious","shouting",
            "sports_commentary","sports_commentary_excited","whispering",
            "terrified","unfriendly"
        ]

        self.LANGLIST = {
            'en-GB-RyanNeural': ['cheerful', 'chat'], 
            'en-GB-SoniaNeural': ['cheerful', 'sad'], 
            'en-US-AriaNeural': ['chat', 'customerservice', 'narration-professional', 'newscast-casual', 'newscast-formal', 'cheerful', 'empathetic', 'angry', 'sad', 'excited', 'friendly', 'terrified', 'shouting', 'unfriendly', 'whispering', 'hopeful'], 
            'en-US-DavisNeural': ['chat', 'angry', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering'], 
            'en-US-GuyNeural': ['newscast', 'angry', 'cheerful', 'sad', 'excited', 'friendly', 'terrified', 'shouting', 'unfriendly', 'whispering', 'hopeful'], 
            'en-US-JaneNeural': ['angry', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering'], 
            'en-US-JasonNeural': ['angry', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering'], 
            'en-US-JennyNeural': ['assistant', 'chat', 'customerservice', 'newscast', 'angry', 'cheerful', 'sad', 'excited', 'friendly', 'terrified', 'shouting', 'unfriendly', 'whispering', 'hopeful'], 
            'en-US-NancyNeural': ['angry', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering'], 
            'en-US-SaraNeural': ['angry', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering'], 
            'en-US-TonyNeural': ['angry', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering'], 
            'es-MX-JorgeNeural': ['cheerful', 'chat'], 
            'fr-FR-DeniseNeural': ['cheerful', 'sad'], 
            'fr-FR-HenriNeural': ['cheerful', 'sad'], 
            'it-IT-IsabellaNeural': ['cheerful', 'chat'], 
            'ja-JP-NanamiNeural': ['chat', 'customerservice', 'cheerful'], 
            'pt-BR-FranciscaNeural': ['calm'], 
            'zh-CN-XiaohanNeural': ['calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad', 'gentle', 'affectionate', 'embarrassed'], 
            'zh-CN-XiaomengNeural': ['chat'], 
            'zh-CN-XiaomoNeural': ['embarrassed', 'calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad', 'depressed', 'affectionate', 'gentle', 'envious'], 
            'zh-CN-XiaoruiNeural': ['calm', 'fearful', 'angry', 'sad'], 
            'zh-CN-XiaoshuangNeural': ['chat'], 
            'zh-CN-XiaoxiaoNeural': ['assistant', 'chat', 'customerservice', 'newscast', 'affectionate', 'angry', 'calm', 'cheerful', 'disgruntled', 'fearful', 'gentle', 'lyrical', 'sad', 'serious', 'poetry-reading'], 
            'zh-CN-XiaoxuanNeural': ['calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'gentle', 'depressed'], 
            'zh-CN-XiaoyiNeural': ['angry', 'disgruntled', 'affectionate', 'cheerful', 'fearful', 'sad', 'embarrassed', 'serious', 'gentle'], 
            'zh-CN-XiaozhenNeural': ['angry', 'disgruntled', 'cheerful', 'fearful', 'sad', 'serious'], 
            'zh-CN-YunfengNeural': ['angry', 'disgruntled', 'cheerful', 'fearful', 'sad', 'serious', 'depressed'], 
            'zh-CN-YunhaoNeural': ['advertisement-upbeat'], 
            'zh-CN-YunjianNeural': ['Narration-relaxed', 'Sports_commentary', 'Sports_commentary_excited'], 
            'zh-CN-YunxiaNeural': ['calm', 'fearful', 'cheerful', 'angry', 'sad'], 
            'zh-CN-YunxiNeural': ['narration-relaxed', 'embarrassed', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad', 'depressed', 'chat', 'assistant', 'newscast'], 
            'zh-CN-YunyangNeural': ['customerservice', 'narration-professional', 'newscast-casual'], 
            'zh-CN-YunyeNeural': ['embarrassed', 'calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad'], 
            'zh-CN-YunzeNeural': ['calm', 'fearful', 'cheerful', 'disgruntled', 'serious', 'angry', 'sad', 'depressed', 'documentary-narration']
            }

    @aiocache.cached(ttl=36000)
    async def genAudioVoice(self,voice_name='zh-CN-XiaohanNeural',context="",style="",speed=-10.00,pitch=-12.00,bg:dict={})->bytes:
        speech_config = speechsdk.SpeechConfig(
            subscription=self.Subscription,
            region=self.region
        )
        
        if not style:
            style = random.choice(self.STYLELIST)
        
        if bg and bg.get("url"):
            bgd = f"""<mstts:backgroundaudio src="{bg.get("url")}" volume="{bg.get("volume",1)}" fadein="{bg.get("fadein",0)}" fadeout="{bg.get("fadeout",0)}"/>"""
        else:
            bgd = ""
        context = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
                    {bgd if bgd else ""}
                    <voice name="{voice_name}">
                        <prosody rate="{speed}%" pitch="{pitch}%">
                            <mstts:express-as style="{style}">
                                {context}
                            </mstts:express-as>
                        </prosody>
                        
                    </voice>
                </speak>
        """
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, 
            audio_config=None
        )
        rendered_bytes = await asyncio.to_thread(synthesizer.speak_ssml_async,context)
        rendered_bytes2:speechsdk.SpeechSynthesisResult = await asyncio.to_thread(rendered_bytes.get)
                
        return rendered_bytes2.audio_data

class Translate:
    """翻译模块"""
    def __init__(self, Subscription,version="",region="") -> None:
        self.Subscription = Subscription
        self.root = "https://api.cognitive.microsofttranslator.com/translate"
        self.region = region
        if version:
            self.version = version
        else: 
            self.version = "3.0"
        self.Langs = [
            'af', 'am', 'ar', 
            'as', 'az', 'ba', 'bg', 
            'bn', 'bo', 'bs', 'ca', 
            'cs', 'cy', 'da', 'de', 
            'dv', 'el', 'en', 'es', 
            'et', 'eu', 'fa', 'fi', 
            'fil', 'fj', 'fo', 'fr', 
            'fr-CA', 'ga', 'gl', 'gu', 
            'he', 'hi', 'hr', 'hsb', 
            'ht', 'hu', 'hy', 'id', 
            'ikt', 'is', 'it', 'iu', 
            'iu-Latn', 'ja', 'ka', 'kk', 
            'km', 'kmr', 'kn', 'ko', 'ku', 
            'ky', 'lo', 'lt', 'lv', 'lzh', 
            'mg', 'mi', 'mk', 'ml', 'mn-Cyrl', 
            'mn-Mong', 'mr', 'ms', 'mt', 'mww', 
            'my', 'nb', 'ne', 'nl', 'or', 'otq', 
            'pa', 'pl', 'prs', 'ps', 'pt', 
            'pt-PT', 'ro', 'ru', 'sk', 'sl', 
            'sm', 'so', 'sq', 'sr-Cyrl', 
            'sr-Latn', 'sv', 'sw', 'ta', 'te', 
            'th', 'ti', 'tk', 'tlh-Latn', 
            'tlh-Piqd', 'to', 'tr', 'tt', 'ty', 
            'ug', 'uk', 'ur', 'uz', 'vi', 'yua', 
            'yue', 'zh-Hans', 'zh-Hant', 'zu',"zh"
        ]
    @aiocache.cached(ttl=3000)
    async def Translate(self,orgin="",target="en",text="",ifprofanityAction=True):


        param = {
            "to":target,
            "api-version":self.version
        }
        if orgin:
            param["from"] = orgin
        if ifprofanityAction:
            param["profanityAction"] = "Marked"

        header = {
            "Ocp-Apim-Subscription-Key":self.Subscription,
            "Ocp-Apim-Subscription-Region":self.region
        }
        js = [{
            "text": text
        }]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url=self.root,params=param,headers=header,json=js) as resp:
                    if resp.status == 200:
                        return (await resp.json())[0]["translations"][0]["text"]
                    return ""
            except:
                return ""

