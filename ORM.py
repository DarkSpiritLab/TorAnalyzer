import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
import RabbitMQ
import json

config = RabbitMQ.getConfig()

'''
sqlalchemy engine
'''
engine = create_engine(config["sqlFilePath"], echo = False)
Base = declarative_base()


class ConnectionLink(Base):
    # (id,datetime,url,client,link1,link2,link3,linkmid,link4,link5,link6,server)
    __tablename__ = "connectionlinks"
    request_id = Column(Integer, primary_key = True, nullable = False)
    url_id = Column(Integer, ForeignKey('urls.url_id'))

    datetime = Column(DateTime)

    client = Column(String, nullable = False)
    link1 = Column(Integer, ForeignKey('links.id'))
    link2 = Column(Integer, ForeignKey('links.id'))
    link3 = Column(Integer, ForeignKey('links.id'))

    linkmid = Column(Integer, ForeignKey('links.id'))

    link4 = Column(Integer, ForeignKey('links.id'))
    link5 = Column(Integer, ForeignKey('links.id'))
    link6 = Column(Integer, ForeignKey('links.id'))

    server = Column(String)

    def __repr__(self):
        return "<ConnectionLink(request_id='%s',datetime='%s',url_id=%s,(client):%s->%s(server))>" % (
            self.request_id, self.datetime, self.url_id, self.client, self.server)

    def toJson(self):
        return json.dumps({c.name: getattr(self, c.name, None) for c in self.__table__.columns})


class Link(Base):
    # # id,datetime,my_ip,next_ip,next_port,prev_circ_id,next_circ_id,direction,stream_id,is_origin,url
    __tablename__ = "links"
    id = Column(Integer, primary_key = True, nullable = False)
    request_id = Column(Integer, nullable = True)
    url_id = Column(Integer, ForeignKey('urls.url_id'))
    datetime = Column(DateTime)
    prev_circ_id = Column(Integer)
    next_circ_id = Column(Integer)
    my_ip = Column(String)
    next_ip = Column(String)
    next_port = Column(Integer)
    direction = Column(Integer)
    stream_id = Column(Integer)
    is_origin = Column(Integer)

    def __repr__(self):
        return "<Link(request_id='%s',datetime='%s',my_ip=%s,next_ip=%s>" % (
            self.request_id, self.datetime, self.my_ip, self.next_ip)


class Url(Base):
    __tablename__ = "urls"
    # id,url,server_ip
    url_id = Column(Integer, primary_key = True, nullable = False)
    url = Column(String, nullable = False)
    server_ip = Column(String, nullable = True)

    def __repr__(self):
        return "<Url(url_id='%s',url='%s',server_ip='%s')>" % (self.url_id, self.url, self.server_ip)

    def toJson(self):
        return json.dumps({c.name: getattr(self, c.name, None) for c in self.__table__.columns})


class Cell(Base):
    __tablename__ = "cells"
    cell_id = Column(Integer, primary_key = True, nullable = False)
    my_ip = Column(String, nullable = False)
    cell = Column(String, nullable = True)

    def __repr__(self):
        return "<Cell(cell_id='%s',my_ip=Column>"


Base.metadata.create_all(engine)
