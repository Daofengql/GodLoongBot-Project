# coding: utf-8
from sqlalchemy import Column, DateTime, JSON, String, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


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
