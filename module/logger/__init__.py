from library.orm.extra import mysql_db_pool
from library.orm.table import Logger
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.model import Group
from graia.ariadne.message.element import Source
import datetime
from sqlalchemy import insert
import pickle
from io import BytesIO


logger = Channel.current()
logger.name("消息记录插件")
logger.author("道锋潜鳞")
logger.description("记录机器人所有群聊聊天数据")

db = mysql_db_pool()

async def dumping(messagechain:MessageChain):
    b = BytesIO()
    pickle.dump(messagechain,b)
    b.seek(0)
    return b.read()

@logger.use(
    ListenerSchema(
        listening_events=[GroupMessage]
        )
    )
async def sign(
    message: MessageChain,
    event:GroupMessage,
    group: Group):
    
    msgid = event.message_chain.get_first(Source).id
    dbsession = await db.get_db_session()
    msg = await dumping(message)
    
    try:
        async with dbsession() as session:
            await session.execute(
                insert(Logger).values(
                    qq = event.sender.id,
                    group=group.id,
                    msgid =msgid,
                    msg=msg,
                    sendtime = datetime.datetime.now()
                )
            )
            await session.commit()
    except:
        pass

