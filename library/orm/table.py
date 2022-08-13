from sqlalchemy import Column, Integer, DateTime, BIGINT, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Sequence, String, DateTime, BigInteger, Boolean, Float, VARCHAR, SMALLINT, DATETIME, BIGINT, INT, SmallInteger, func, TEXT
import datetime
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






class Sign_in(Base):
    __tablename__ = 'signin'
    id = Column(INT,nullable=False, primary_key=True, autoincrement=True, comment="id")
    qq = Column(BIGINT,nullable=False, primary_key=True,comment="用户qq")
    lastdate = Column(DateTime,nullable=False, default=datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S"),comment="签到日期")
    days = Column(INT,nullable=False,default=0, comment="签到天数")
    coin = Column(BIGINT,nullable=False,default=0,comment="用户签到积分")
    
    
class Logger(Base):
    __tablename__ = 'logger'
    id = Column(BIGINT,nullable=False, primary_key=True, autoincrement=True, comment="id")
    group = Column(BIGINT,nullable=False, primary_key=True,comment="群号")
    qq = Column(BIGINT,nullable=False, primary_key=True,comment="发信QQ")
    msgid = Column(BIGINT,nullable=False, primary_key=True,comment="消息编号")
    msg = Column(TEXT,nullable=False,comment="消息内容")
    msgimage = Column(TEXT,nullable=True, comment="消息编号")
    sendtime = Column(DateTime,nullable=False, default=datetime.datetime.now(),comment="签到日期")