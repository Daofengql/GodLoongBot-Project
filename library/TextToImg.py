from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import re
from pathlib import Path
import string

ttfname ="HarmonyOS_Sans/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Medium.ttf"

class AsyncTextToImage(object):
    def __init__(self,) -> None:
        
        font_file =font_file = str(Path(Path(__file__).parent.parent, "library","assets", "fonts", ttfname))
        try:
            self.font = ImageFont.truetype(font_file, 22)
        except OSError:pass

        
    async def get_cut_str_sync(self,str, cut)->list:
        """
        自动断行，用于 Pillow 等不会自动换行的场景
        """
        punc = """，,、。.？?）》】“"‘'；;：:！!·`~%^& """
        si = 0
        i = 0
        next_str = str
        str_list = []

        while re.search(r"\n\n\n\n\n", next_str):
            next_str = re.sub(r"\n\n\n\n\n", "\n", next_str)
        for s in next_str:
            if s in string.printable:
                si += 1
            else:
                si += 2
            i += 1
            if next_str == "":
                break
            elif next_str[0] == "\n":
                next_str = next_str[1:]
            elif s == "\n":
                str_list.append(next_str[: i - 1])
                next_str = next_str[i - 1 :]
                si = 0
                i = 0
                continue
            if si > cut:
                try:
                    if next_str[i] in punc:
                        i += 1
                except IndexError:
                    str_list.append(next_str)
                    return str_list
                str_list.append(next_str[:i])
                next_str = next_str[i:]
                si = 0
                i = 0
        str_list.append(next_str)
        i = 0
        non_wrap_str = []
        for p in str_list:
            if p == "":
                break
            elif p[-1] == "\n":
                p = p[:-1]
            non_wrap_str.append(p)
            i += 1
        return non_wrap_str



    async def create_image_sync(self,text: str, cut: int) -> BytesIO:
        cut_str = "\n".join(await self.get_cut_str_sync(text, cut))
        textx, texty = self.font.getsize_multiline(cut_str)
        image = Image.new("RGB", (textx + 40, texty + 40), (235, 235, 235))
        draw = ImageDraw.Draw(image)
        draw.text((20, 20), cut_str, font=self.font, fill=(31, 31, 33))
        imageio = BytesIO()
        image.save(
            imageio,
            format="JPEG",
            quality=90,
            subsampling=2,
            qtables="web_high",
        )
        imageio.seek(0)
        return imageio


class TextToImage(object):
    def __init__(self) -> None:
        font_file =font_file = str(Path(Path(__file__).parent.parent, "library","assets", "fonts", ttfname))
        try:
            self.font = ImageFont.truetype(font_file, 22)
        except OSError:pass

    def get_cut_str(self,str, cut)->list:
        """
        自动断行，用于 Pillow 等不会自动换行的场景
        """
        punc = """，,、。.？?）》】“"‘'；;：:！!·`~%^& """
        si = 0
        i = 0
        next_str = str
        str_list = []

        while re.search(r"\n\n\n\n\n", next_str):
            next_str = re.sub(r"\n\n\n\n\n", "\n", next_str)
        for s in next_str:
            if s in string.printable:
                si += 1
            else:
                si += 2
            i += 1
            if next_str == "":
                break
            elif next_str[0] == "\n":
                next_str = next_str[1:]
            elif s == "\n":
                str_list.append(next_str[: i - 1])
                next_str = next_str[i - 1 :]
                si = 0
                i = 0
                continue
            if si > cut:
                try:
                    if next_str[i] in punc:
                        i += 1
                except IndexError:
                    str_list.append(next_str)
                    return str_list
                str_list.append(next_str[:i])
                next_str = next_str[i:]
                si = 0
                i = 0
        str_list.append(next_str)
        i = 0
        non_wrap_str = []
        for p in str_list:
            if p == "":
                break
            elif p[-1] == "\n":
                p = p[:-1]
            non_wrap_str.append(p)
            i += 1
        return non_wrap_str



    def create_image(self,text: str, cut: int) -> BytesIO:
        cut_str = "\n".join(self.get_cut_str(text, cut))
        textx, texty = self.font.getsize_multiline(cut_str)
        image = Image.new("RGB", (textx + 40, texty + 40), (235, 235, 235))
        draw = ImageDraw.Draw(image)
        draw.text((20, 20), cut_str, font=self.font, fill=(31, 31, 33))
        imageio = BytesIO()
        image.save(
            imageio,
            format="JPEG",
            quality=90,
            subsampling=2,
            qtables="web_high",
        )
        imageio.seek(0)
        return imageio
        