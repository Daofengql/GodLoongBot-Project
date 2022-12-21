from typing import List, Optional,Any
from pydantic import BaseModel

class ips(object): 
    class Cz88(BaseModel):
        ip: str
        range: str
        address: str
        country: str
        isp: str