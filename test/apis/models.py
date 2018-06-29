from test.database import SurrogatePK, Model, db
from sqlalchemy import Column, String,DateTime, Integer


class UserInfo(SurrogatePK, Model):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    uid = Column(String(255))
    address = Column(String(255))
    create_time = Column(DateTime)
    open_id = Column(String(255))
    avatar = Column(String(255))
    price = Column(String(10))
    number = Column(String(10))
    paihang = Column(String(255))
    cash = Column(String(10))
class TokenItem(SurrogatePK,Model):
    __tablename__ = 'token_item'
    id = Column(Integer,primary_key=True)
    open_id = Column(String(255))
    tokenname = Column(String(255))
    dui = Column(String(255))
    numbers = Column(String(10))
    zhanbi = Column(String(10))