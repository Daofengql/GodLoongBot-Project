import os
import json
class bot(object):
    def __init__(self):
        with open(os.getcwd()+"/library/weijinci.txt",'r',encoding='utf-8',errors='ignore') as f:
            self.weijingci = json.loads(f.read())
    
