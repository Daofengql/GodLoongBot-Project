import xmltojson
from library.config import config
from library.orm.table import Sub
from library.Bot import bot
from library.orm.extra import mysql_db_pool


db = mysql_db_pool()
bot = bot()

async def parse_eq_data(xml_CEIC:str) -> list:
    tmp = xmltojson.xmltodict.parse(xml_CEIC)
    result = []
    del(tmp["Workbook"]["Worksheet"]["Table"]["Row"][0])
    for row in tmp["Workbook"]["Worksheet"]["Table"]["Row"]:
        row = row["Cell"]
        result.append(
            {
                "time":row[0]["Data"]["#text"],
                "level":float(row[1]["Data"]["#text"]),
                "longitude":float(row[2]["Data"]["#text"]),
                "latitude":float(row[3]["Data"]["#text"]),
                "depth":float(row[4]["Data"]["#text"]),
                "addr":row[5]["Data"]["#text"]
            }
        )
    return result

async def get_sub_group(func:str):
    dbsession = await db.get_db_session()
    async with dbsession() as session:
        pass
    if func == "eq":
        #返回地震播报订阅群列表
        return [438991075]