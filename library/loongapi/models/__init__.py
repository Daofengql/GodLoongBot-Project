from typing import List, Optional,Any
from pydantic import BaseModel
from .Results import Results
from .et.stellaris.species import species

class Model_ret(BaseModel):
    code: Optional[int] = None
    result: Optional[
        Results.song_Result
        |Results.Tool_IP_Result
        |species.GetALLCont_ret_Result
        |species.Random_ret_Result
        ] = None
    message: Optional[str] = None