from typing import List, Optional,Any
from pydantic import BaseModel

class Song_types(object):

    class Song_netease(BaseModel):
        class AuthorItem(BaseModel):
            id: int
            name: str
            tns: List
            alias: List
        name: str
        id: int
        picurl: str
        songurl: str
        author: List[AuthorItem]


    class Song_kugo(BaseModel):
        name: Optional[str] = None
        id: Optional[str] = None
        author: Optional[str] = None
        audio_id: Optional[int] = None