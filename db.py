#!/usr/bin/env python

from sqlalchemy import Column, DateTime, String, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import sessionmaker

import config

Base = declarative_base()

class Codes(Base):
    __tablename__ = 'codes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String)

class SenderAccount(Base):
    __tablename__ = 'sender_account'
    
    id = Column(mysql.BIGINT, primary_key=True)
    sender_twitter_id = Column(mysql.BIGINT)
    sender_twitter_handle = Column(String)
    gco_internal_id = Column(String)
    triggered_from = Column(String)
    sender_data = Column(Text)
    created_at = Column(DateTime)

class SenderFollowing(Base):
    __tablename__ = 'sender_following'

    id = Column(mysql.BIGINT, primary_key=True)
    sender_twitter_id = Column(mysql.BIGINT)
    following = Column(Text)
    created_at = Column(DateTime)

class TwitterIdToHandle(Base):
    __tablename__ = 'twitter_id_to_handle'
    
    id = Column(Integer, primary_key=True)
    twitter_id = Column(mysql.BIGINT)
    twitter_handle = Column(String)

class Operations(Base):
    __tablename__ = 'operations'

    id = Column(mysql.BIGINT, primary_key=True)
    account = Column(String)
    is_closed = Column(Boolean)
    user_id = Column(mysql.BIGINT) #current only for twitter
    user_gco_internal_id = Column(String)
    code = Column(String)
    reply_code = Column(String)
    pin = Column(String)
    url = Column(String)
    media = Column(String)
    created_at = Column(DateTime)
    timeout_at = Column(DateTime)
    reply_ack = Column(Boolean)
    click_ack = Column(Boolean)
    source = Column(String)

engine = create_engine("mysql://%s:%s@localhost/%s" % (config.DB_USER, config.DB_PWD, config.DB_NAME), echo=False, pool_recycle=3600)

def get_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session

if __name__ == "__main__":
    get_session()

