
import xmltojson
import aiocache
from library.config import config
from library.orm.table import Sub
from library.Bot import bot
from library.orm.extra import mysql_db_pool
from sqlalchemy import select, insert,delete

db = mysql_db_pool()
bot = bot()


@aiocache.cached(ttl=3600)
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
        first = await session.execute(
            select(Sub)
            .where( Sub.subfuc == func)
        )
        first: list[Sub] = first.scalars().all()
        return [group.group for group in first]


async def change_sub_status(func:str,group:int,status:str) -> bool:
    """返回TRUE表示已经开启，返回False表示已经关闭"""
    dbsession = await db.get_db_session()
    async with dbsession() as session:
        if status == "enable":
            first = await session.execute(
                select(Sub)
                .where( Sub.subfuc == func,Sub.group == group)
            )
            first: list[Sub] = first.scalars().all()
            if first:
                return True
            else:
                await session.execute(
                    insert(Sub).values(
                        group = group,
                        subfuc = func
                    )
                )
                await session.commit()
                return True

        elif status == "status":
            first = await session.execute(
                select(Sub)
                .where( Sub.subfuc == func,Sub.group == group)
            )
            first: list[Sub] = first.scalars().all()
            if first:
                return True
            else:
                return False
        
        elif status == "disable":
            first = await session.execute(
                select(Sub)
                .where( Sub.subfuc == func,Sub.group == group)
            )
            first: list[Sub] = first.scalars().all()
            if not first:
                return False
            else:

                await session.execute(
                    delete(Sub)
                    .where(Sub.subfuc == func,Sub.group == group)
                )
                await session.commit()
                return False


            

