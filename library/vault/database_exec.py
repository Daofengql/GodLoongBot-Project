from ..orm.table import User
from ..orm.extra import mysql_db_pool

from sqlalchemy.sql import select, insert, delete

import asyncio
import datetime,uuid

class QQNotFoundERR(Exception):
    """无法获取到QQ"""
    def __str__(self):
        return repr("无法获取到QQ,无法查询对应关系")


class UserNotFoundERR(Exception):
    """无法获取到用户"""
    def __str__(self):
        return repr("无法获取到用户,无法查询对应关系")

class dbexec(object):
    def __init__(self) -> None:
        self.mydb = mysql_db_pool()

    async def getUserProfile(self,userQQ,userGroup=0)->list[User]:
        if not userQQ :
            raise QQNotFoundERR

        dbsession = await self.mydb.get_db_session()
        async with dbsession() as session:
            # 读取用户是否存在
            first = await session.execute(
                select(User)
                .where(User.qq == userQQ, User.group == userGroup)
            )
            first = first.scalars().all()
        return first
    
    async def modifyUserProfile(
        self,
        id:int = 0,
        qq:int = 0,
        group:int = 0,
        nickname:str = "",
        coin:int = 0,
        iron:int = 0,
        unity:int = 0,
        species:int = 0
    )->bool:
        if id:
            sql = (select(User)
            .where(User.id == id)
            .with_for_update()
            .limit(1))
        else:
            sql = (select(User)
            .where(User.qq == qq,User.group == group)
            .with_for_update()
            .limit(1))
        dbsession = await self.mydb.get_db_session()
        async with dbsession() as session:
            data = await session.execute(sql)
            data:list[User] = data.scalars().all()
            if not data:
                raise UserNotFoundERR
            
            data = data[0]
            data.coin = coin
            data.nickname = nickname
            data.species = species
            data.iron = iron
            data.unity = unity
            await session.commit()
            return True

    async def insertUserProfile(
        self,
        qq:int = 0,
        group:int = 0,
        nickname:str = "",
        coin:int = 0,
        iron:int = 0,
        unity:int = 0,
        species:int = 0
    )->bool:     
        dbsession = await self.mydb.get_db_session()
        async with dbsession() as session:
            await session.execute(
                    insert(User).values(
                        qq=qq,
                        group=group,
                        lasttime=datetime.datetime.strptime(
                            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
                            "%Y-%m-%d %H:%M:%S",
                        ),
                        coin=coin,
                        nickname=nickname,
                        iron=iron,
                        unity=unity,
                        species=species
                    ))
            await session.commit()
            return True
    async def delUserProfile(
        self,
        id:int = 0,
        qq:int = 0,
        group:int = 0
    )->bool:  
        if id:
            sql = delete(User).where(User.id == id)
        else:
            sql = delete(User).where(User.qq == qq, User.group == group)
        dbsession = await self.mydb.get_db_session()
        async with dbsession() as session:
            await session.execute(sql)
            await session.commit()
            return True

    
    async def getGroupRank(
        self,
        group, 
        types
    )->list[User]:
        dbsession = await self.mydb.get_db_session()
        async with dbsession() as session:
            if types in ("", "综合排名"):
                first = await session.execute(
                    select(User)
                    .where(User.group == group)
                    .order_by(
                        (
                            ((User.coin * 10) + (User.iron * 15000) + (User.unity * 5))/1000
                        ).desc()
                    )
                    .limit(6)
                )
            elif types in ("能量币排行"):
                first = await session.execute(
                    select(User)
                    .where(User.group == group)
                    .order_by(User.coin.desc())
                    .limit(6)
                )
            elif types in ("合金排行"):
                first = await session.execute(
                    select(User)
                    .where(User.group == group)
                    .order_by(User.iron.desc())
                    .limit(6)
                )
            elif types in ("凝聚力排行"):
                first = await session.execute(
                    select(User)
                    .where(User.group == group)
                    .order_by(User.unity.desc())
                    .limit(6)
                )
            first: list[User] = first.scalars().all()
        return first




