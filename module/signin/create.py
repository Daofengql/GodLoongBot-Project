# -*- coding:utf-8 -*-

from pathlib import Path
import base64
import datetime

import os
import random
from enum import Enum
from io import BytesIO


import httpx
from dateutil.parser import parse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import json


# ==========================================
RESOURCES_BASE_PATH = str(os.path.dirname(__file__))

# ==========================================
highQuality = False

# ==========================================

class Status(Enum):

    SUCCESS = "_success"

    FAILURE = "_failure"


class Model(Enum):

    ALL = "_all"

    BLURRY = "_blurry"

    SEND_AT = "_send_at"

    SEND_DEFAULT = "_send_default"


class Tools:

    @staticmethod
    def writeFile(p, content):
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def readFileByLine(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return f.readlines()

    @staticmethod
    def readJsonFile(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    @staticmethod
    def writeJsonFile(p, content):
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(content))
        return Status.SUCCESS

    @staticmethod
    def readFileContent(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return f.read().strip()

    @staticmethod
    def readPictureFile(picPath):
        if not os.path.exists(picPath):
            return Status.FAILURE
        with open(picPath, "rb") as f:
            return f.read()

    @classmethod
    def base64conversion(cls, picPath):
        picByte = cls.readPictureFile(picPath)
        if picByte == Status.FAILURE:
            raise Exception("图片文件不存在！")
        return str(base64.b64encode(picByte), encoding="utf-8")

    @staticmethod
    def sendText(userGroup, msg, bot, model=Model.SEND_DEFAULT, atQQ=""):
        if msg not in ("", Status.FAILURE):
            if model == Model.SEND_DEFAULT:
                bot.sendGroupText(userGroup, content=str(msg))
            if model == Model.SEND_AT:
                if atQQ == "":
                    raise Exception("没有指定 at 的人！")
                at = f"[ATUSER({atQQ})]\n"
                bot.sendGroupText(userGroup, content=at + str(msg))

    @staticmethod
    def commandMatch(msg, commandList, model=Model.ALL):
        if model == Model.ALL:
            for c in commandList:
                if c == msg:
                    return True
        if model == Model.BLURRY:
            for c in commandList:
                if msg.find(c) != -1:
                    return True
        return False

    @staticmethod
    def checkFolder(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def atQQ(userQQ):
        return f"[ATUSER({userQQ})]\n"

    class Dict(dict):
        __setattr__ = dict.__setitem__
        __getattr__ = dict.__getitem__

    @classmethod
    def dictToObj(cls, dictObj):
        if not isinstance(dictObj, dict):
            return dictObj
        d = cls.Dict()
        for k, v in dictObj.items():
            d[k] = cls.dictToObj(v)
        return d

    @staticmethod
    def random(items):
        return random.choice(items)


class Network:

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }

    @classmethod
    def getBytes(cls, url, headers="", timeout=10):
        if headers == "":
            headers = cls.DEFAULT_HEADERS
        try:
            return httpx.get(url=url, headers=headers, timeout=timeout).read()
        except:
            return Status.FAILURE

    @classmethod
    def getJson(cls, url, headers="", timeout=10):
        if headers == "":
            headers = cls.DEFAULT_HEADERS
        try:
            return httpx.get(url=url, headers=headers, timeout=timeout).json()
        except:
            return Status.FAILURE


class User:
    def __init__(self, nickname, favorability, days, hitokoto):
        self._userNickname = nickname
        self._userFavorability = favorability
        self._userSignInDays = days
        self._userHitokoto = hitokoto

        self._userInfo = "签 到 成 功"

        self._userInfoIntegration = (
            f"签到天数  {self._userSignInDays}   麟币余额  {self._userFavorability}"
        )


class SignIn(User):

    FONT_REEJI = "REEJI-HonghuangLiGB-SemiBold.ttf"

    FONT_ZHANKU = "zhanku.ttf"

    def __init__(
        self,
        userQQ,
        nickname,
        favorability,
        days,
        hitokoto,
        basemapSize=640,
        avatarSize=256,
    ):

        super().__init__(nickname, favorability, days, hitokoto)

        self._userQQ = userQQ
        self._basemapSize = basemapSize
        self._avatarSize = avatarSize

        self._img = Status.FAILURE
        self._roundImg = Status.FAILURE
        self._canvas = Status.FAILURE
        self._magicCircle = Status.FAILURE
        self._textBaseMap = Status.FAILURE

        self._magicCirclePlus = 30
        self._avatarVerticalOffset = 50
        self._textBaseMapSize = (540, 160)
        self._topPositionOfTextBaseMap = 425
        self._textBaseMapLeftPosition = int(
            (self._basemapSize - self._textBaseMapSize[0]) / 2
        )
        self._fontAttenuation = 2
        self._minimumFontLimit = 10
        self._infoCoordinatesY = Tools.dictToObj(
            {
                "nickname": self._topPositionOfTextBaseMap + 26,
                "info": self._topPositionOfTextBaseMap + 64,
                "integration": self._topPositionOfTextBaseMap + 102,
                "hitokoto": self._topPositionOfTextBaseMap + 137,
            }
        )
        self._infoFontSize = Tools.dictToObj(
            {"nickname": 28, "info": 28, "integration": 25, "hitokoto": 25}
        )
        self._infoFontName = Tools.dictToObj(
            {
                "nickname": self.FONT_REEJI,
                "info": self.FONT_REEJI,
                "integration": self.FONT_REEJI,
                "hitokoto": self.FONT_ZHANKU,
            }
        )

    @staticmethod
    def getPictures(url):
        img = Network.getBytes(url)
        return img

    def createAvatar(self):
        size = self._basemapSize
        avatarImgUrl = "http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640".format(
            QQ=self._userQQ)
        res = self.getPictures(avatarImgUrl)
        self._img = self.resize(Image.open(
            BytesIO(res)).convert("RGBA"), (size, size))
        return self

    @staticmethod
    def resize(img, size):
        return img.copy().resize(size, Image.ANTIALIAS)

    @staticmethod
    def gaussianBlur(img, radius=7):
        return img.copy().filter(ImageFilter.GaussianBlur(radius=radius))

    @staticmethod
    def imageRadiusProcessing(img, centralA, radius=30):
        """处理图片四个圆角。
        :centralA: 中央区域的 A 通道值，当指定为 255 时全透，四角将使用 0 全不透
        """
        circle = Image.new("L", (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=centralA)
        w, h = img.size
        alpha = Image.new("L", img.size, centralA)
        upperLeft, lowerLeft = circle.crop((0, 0, radius, radius)), circle.crop(
            (0, radius, radius, radius * 2)
        )
        upperRight, lowerRight = (
            circle.crop((radius, 0, radius * 2, radius)),
            circle.crop((radius, radius, radius * 2, radius * 2)),
        )
        alpha.paste(upperLeft, (0, 0))
        alpha.paste(upperRight, (w - radius, 0))
        alpha.paste(lowerRight, (w - radius, h - radius))
        alpha.paste(lowerLeft, (0, h - radius))
        img.putalpha(alpha)
        return img

    def createRoundImg(self):
        img = self._img
        size = self._avatarSize

        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)

        self._roundImg = self.resize(img, (size, size))
        self._roundImg.putalpha(mask)
        return self

    def createCanvas(self):
        size = self._basemapSize
        self._canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self._canvas.paste(self.gaussianBlur(self._img))
        return self

    def createAMagicCircle(self):
        size = self._magicCirclePlus + self._avatarSize
        magicCircle = Image.open(
            f"{RESOURCES_BASE_PATH}/magic-circle.png").convert("L")
        magicCircle = self.resize(magicCircle, (size, size))
        self._magicCircle = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self._magicCircle.putalpha(magicCircle)
        return self

    def createTextBasemap(self, transparency=190):
        self._textBaseMap = Image.new(
            "RGBA", self._textBaseMapSize, (0, 0, 0, transparency)
        )
        self._textBaseMap = self.imageRadiusProcessing(
            self._textBaseMap, transparency)
        return self

    def additionalMagicCircle(self):
        magicCircle = self._magicCircle
        x = int((self._basemapSize - self._avatarSize - self._magicCirclePlus) / 2)
        y = x - self._avatarVerticalOffset
        self._canvas.paste(magicCircle, (x, y), magicCircle)
        return self

    def additionalAvatar(self):
        avatar = self._roundImg
        x = int((self._basemapSize - self._avatarSize) / 2)
        y = x - self._avatarVerticalOffset
        self._canvas.paste(avatar, (x, y), avatar)
        return self

    def additionalTextBaseMap(self):
        textBaseMap = self._textBaseMap
        x = int((self._basemapSize - self._textBaseMapSize[0]) / 2)
        y = self._topPositionOfTextBaseMap
        self._canvas.paste(textBaseMap, (x, y), textBaseMap)
        return self

    def writePicture(
        self, img, text, position, fontName, fontSize, color=(255, 255, 255)
    ):
        font = ImageFont.truetype(
            f"{RESOURCES_BASE_PATH}/font/{fontName}", fontSize)
        draw = ImageDraw.Draw(img)
        textSize = font.getsize(text)
        attenuation = self._fontAttenuation
        x = int(position[0] - textSize[0] / 2)
        limit = self._minimumFontLimit
        while x <= self._textBaseMapLeftPosition:
            fontSize -= attenuation
            if fontSize <= limit:
                return Status.FAILURE
            font = ImageFont.truetype(
                f"{RESOURCES_BASE_PATH}/font/{fontName}", fontSize
            )
            textSize = font.getsize(text)
            x = int(position[0] - textSize[0] / 2)
        y = int(position[1] - textSize[1] / 2)
        draw.text((x, y), text, color, font=font)
        return Status.SUCCESS

    def additionalSignInInformation(self):
        fontSize = self._infoFontSize
        coordinateY = self._infoCoordinatesY
        font = self._infoFontName
        x = int(self._basemapSize / 2)
        # Add user nickname
        result = self.writePicture(
            img=self._canvas,
            text=self._userNickname,
            position=(x, coordinateY.nickname),
            fontName=font.nickname,
            fontSize=fontSize.nickname,
        )
        if result == Status.FAILURE:
            return Status.FAILURE
        # Add success message
        result = self.writePicture(
            img=self._canvas,
            text=self._userInfo,
            position=(x, coordinateY.info),
            fontName=font.info,
            fontSize=fontSize.info,
        )
        if result == Status.FAILURE:
            return Status.FAILURE
        # Add integration information
        result = self.writePicture(
            img=self._canvas,
            text=self._userInfoIntegration,
            position=(x, coordinateY.integration),
            fontName=font.integration,
            fontSize=fontSize.integration,
        )
        if result == Status.FAILURE:
            return Status.FAILURE
        # Addition hitokoto
        result = self.writePicture(
            img=self._canvas,
            text=self._userHitokoto,
            position=(x, coordinateY.hitokoto),
            fontName=font.hitokoto,
            fontSize=fontSize.hitokoto,
        )
        if result == Status.FAILURE:
            return Status.FAILURE
        return self

    def save(self)->BytesIO:
        imageio = BytesIO()
        global highQuality
        if highQuality:
            self._canvas.save(
                imageio,
                format="PNG",
            )
        else:
            self._canvas.convert("RGB").save(
                imageio,
                format="JPEG",
                quality=60,
                subsampling=2,
                qtables="web_high",
            )
        imageio.seek(0)
        return imageio

    def drawing(self):
        # Start generating
        result = (
            self.createAvatar()
            .createRoundImg()
            .createCanvas()
            .createAMagicCircle()
            .createTextBasemap()
            # Start processing
            .additionalMagicCircle()
            .additionalAvatar()
            .additionalTextBaseMap()
            # Must be the last step
            .additionalSignInInformation()
        )
        if result == Status.FAILURE:
            return result
        # Sav
        return result.save()


class TimeUtils:

    DAY = "day"

    HOUR = "hour"

    MINUTE = "minute"

    SECOND = "second"

    ALL = "all"

    @staticmethod
    def getTheCurrentTime():
        """%Y-%m-%d 格式的日期"""
        nowDate = str(datetime.datetime.strftime(
            datetime.datetime.now(), "%Y-%m-%d"))
        return nowDate

    @staticmethod
    def getAccurateTimeNow():
        """%Y-%m-%d/%H:%M:%S 格式的日期"""
        nowDate = str(
            datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d/%H:%M:%S")
        )
        return nowDate

    @classmethod
    def judgeTimeDifference(cls, lastTime):
        """获取时间差小时"""
        timeNow = cls.getAccurateTimeNow()
        a = parse(lastTime)
        b = parse(timeNow)
        return int((b - a).total_seconds() / 3600)

    @staticmethod
    def getTheCurrentHour():
        """获取当前小时 %H"""
        return int(str(datetime.datetime.strftime(datetime.datetime.now(), "%H")))

    @classmethod
    def getTimeDifference(cls, original, model):
        """
        :model: ALL [天数差, 小时差, 分钟零头, 秒数零头] \n
        :model: DAY 获取天数差 \n
        :model: MINUTE 获取分钟差 \n
        :model: SECOND 获取秒数差
        """
        a = parse(original)
        b = parse(cls.getAccurateTimeNow())
        seconds = int((b - a).total_seconds())
        if model == cls.ALL:
            return {
                cls.DAY: int((b - a).days),
                cls.HOUR: int(seconds / 3600),
                cls.MINUTE: int((seconds % 3600) / 60),  # The rest
                cls.SECOND: int(seconds % 60),  # The rest
            }
        if model == cls.DAY:
            b = parse(cls.getTheCurrentTime())
            return int((b - a).days)
        if model == cls.MINUTE:
            return int(seconds / 60)
        if model == cls.SECOND:
            return seconds

def generatePicture(userQQ, nickname, coins, days, hitokoto):
    result = SignIn(userQQ, nickname, coins, days, hitokoto).drawing()
    return result

