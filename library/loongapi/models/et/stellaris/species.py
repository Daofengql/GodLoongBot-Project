from typing import List, Optional,Any
from pydantic import BaseModel

class species(object): 
    class Random_ret_Result(BaseModel):
        name: str
        id: int
        pic: str

    class GetALLCont_ret_Result(BaseModel):
        count: int