from typing import List, Optional,Any
from pydantic import BaseModel

from .SongChoices import Song_types
from .tools.iptools import ips


class Results(object):
    class song_Result(BaseModel):
            songs: List[Song_types.Song_netease|Song_types.Song_kugo]
            count: int
            
    class Tool_IP_Result(BaseModel):
        cz88: ips.Cz88