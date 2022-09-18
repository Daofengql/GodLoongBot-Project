import datetime

from sqlalchemy import Column, Integer, String, DateTime, INT, TEXT, JSON, Text,text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT

from library.orm import Base


class FunctionCallRecord(Base):
    """
    Function call record

    id: Record id
    time: Calling time
    field: Calling field
    supplicant: Calling supplicant
    function: Called module
    """

    __tablename__ = "function_call_record"

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    field = Column(BIGINT, nullable=False)
    supplicant = Column(BIGINT, nullable=False)
    function = Column(String(length=4000), nullable=False)


class BlacklistTable(Base):
    """
    BlacklistTable

    field: Field ID, -1 for global, 0 for direct message, >0 for group
    target: Target ID, 0 for group, >0 for user
    time: Time
    reason: Reason
    supplicant: Supplicant ID
    """

    __tablename__ = "blacklist"

    field = Column(BIGINT, nullable=False, primary_key=True)
    target = Column(BIGINT, nullable=False, primary_key=True)
    time = Column(DateTime, nullable=False)
    reason = Column(String(length=4000), nullable=False)
    supplicant = Column(BIGINT, nullable=False)



class Logger(Base):

    __tablename__ = "logger"

    id = Column(
        BIGINT, nullable=False, primary_key=True, autoincrement=True, comment="id"
    )
    """ ID """

    group = Column(BIGINT, nullable=False, primary_key=True, comment="群号")
    """ 群号 """

    qq = Column(BIGINT, nullable=False, primary_key=True, comment="发信QQ")
    """ 发信QQ """

    msgid = Column(BIGINT, nullable=False, primary_key=True, comment="消息编号")
    """ 消息编号 """

    msg = Column(TEXT, nullable=False, comment="消息内容")
    """ 消息内容 """

    msgimage = Column(TEXT, nullable=True, comment="消息编号")
    """ 消息编号 """

    sendtime = Column(
        DateTime, nullable=False, default=datetime.datetime.now(), comment="签到日期"
    )
    """ 签到日期 """


class BattleLog(Base):
    __tablename__ = 'battle_log'

    id = Column(BIGINT(20), primary_key=True, comment='对局编号')
    winner_group_id = Column(JSON, nullable=False, comment='获胜的舰队')
    loser_group_id = Column(JSON, nullable=False, comment='输掉对局的舰队')
    time = Column(DateTime, nullable=False)


class Fleet(Base):
    __tablename__ = 'fleets'

    id = Column(BIGINT(20), primary_key=True, nullable=False, comment='舰队id')
    uid = Column(BIGINT(20), primary_key=True, nullable=False, comment='对应主人的id')
    nickname = Column(String(30, 'utf8_unicode_ci'), primary_key=True, nullable=False, comment='舰队名')
    group = Column(BIGINT(20), primary_key=True, nullable=False, comment='所属群聊')


class Ship(Base):
    __tablename__ = 'ships'

    id = Column(BIGINT(20), primary_key=True, nullable=False, comment='舰船id')
    uid = Column(BIGINT(20), primary_key=True, nullable=False, comment='对应主人的id')
    group = Column(BIGINT(20), primary_key=True, nullable=False, comment='所属舰队')
    fire = Column(BIGINT(20), nullable=False, comment='火力值')
    type = Column(INTEGER(11), nullable=False, comment='舰船类型')
    isdestroyed = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='是否被摧毁，是为1，不是为0')


class User(Base):
    __tablename__ = 'users'

    id = Column(BIGINT(20), primary_key=True, nullable=False, comment='子账号')
    qq = Column(BIGINT(20), primary_key=True, nullable=False, comment='账号')
    group = Column(BIGINT(20), primary_key=True, nullable=False, comment='所在群聊')
    nickname = Column(String(30, 'utf8_unicode_ci'), primary_key=True, nullable=False, comment='昵称')
    coin = Column(BIGINT(20), nullable=False, server_default=text("'0'"), comment='持有币数')
    iron = Column(BIGINT(20), nullable=False, comment='合金数')
    unity = Column(BIGINT(20), nullable=False, comment='凝聚力')
    lasttime = Column(DateTime, nullable=False)


class Sub(Base):
    __tablename__ = 'sub'

    group = Column(BIGINT(20), primary_key=True, comment='群号')
    subfuc = Column(Text(collation='utf8_unicode_ci'), nullable=False, comment='订阅功能的名称')

