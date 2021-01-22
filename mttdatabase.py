import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from settings import MttSettings

s = MttSettings('db/config.json')

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = '1qa2ws3edfkj589ugfpw905eugp90wug'
app.static_folder = os.getcwd() + '/static'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
separator = '/' if os.name == 'nt' else '//'

try:
    if s.values['db'] == 'sqlite':
        import sqlite3
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite://{ separator }db/mtt.db'
    elif s.values['db'] == 'mysql':
        import pymysql
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            f'mysql+pymysql://{ s.values["sql_user"] }:{ s.values["sql_password"] }@' \
            f'{ s.values["sql_host"] }/{ s.values["sql_db"] }'
    elif s.values['db'] == 'postgresql':
        import psycopg2
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            f'postgresql+psycopg2://{ s.values["sql_user"] }:{ s.values["sql_password"] }@' \
            f'{ s.values["sql_host"] }/{ s.values["sql_db"] }'
    elif s.values['db'] == 'mssql':
        import pyodbc
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            f'mssql+pyodbc://{ s.values["sql_user"] }:{ s.values["sql_password"] }@' \
            f'{ s.values["sql_host"] }/{ s.values["sql_db"] }'
    elif s.values['db'] == 'oracle':
        import cx_Oracle
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            f'oracle+cx_oracle://{ s.values["sql_user"] }:{ s.values["sql_password"] }@' \
            f'{ s.values["sql_host"] }/{ s.values["sql_db"] }'
except ModuleNotFoundError as e:
    print(e)

database = SQLAlchemy(app)


def table_exists(name):
    return database.engine.dialect.has_table(database.engine, name)


class Lists(database.Model):
    __tablename__ = s.values['prefix'] + 'lists'
    id = database.Column(database.Integer, name='id', nullable=False, unique=True, primary_key=True, autoincrement=True)
    uuid = database.Column(database.String(32), name='uuid', unique=True, index=True)
    ow = database.Column(database.Integer, name='ow', nullable=False, default=0)
    name = database.Column(database.String(50), name='name', nullable=False)
    d_created = database.Column(database.Integer, name='d_created', nullable=False, default=0)
    d_edited = database.Column(database.Integer, name='d_edited', nullable=False, default=0)
    sorting = database.Column(database.Integer, name='sorting', nullable=False, default=0)
    published = database.Column(database.Integer, name='published', nullable=False, default=0)
    taskview = database.Column(database.Integer, name='taskview', nullable=False, default=0)

    @classmethod
    def max_ow(cls):
        return database.session.query(func.max(cls.ow)).first()[0] or 0


class Todolist(database.Model):
    __tablename__ = s.values['prefix'] + 'todolist'
    id = database.Column(database.Integer, name='id', nullable=False, unique=True, primary_key=True, autoincrement=True)
    uuid = database.Column(database.String(32), name='uuid', unique=True, index=True)
    list_id = database.Column(database.Integer, name='list_id', nullable=False, default=0, index=True)
    d_created = database.Column(database.Integer, name='d_created', nullable=False, default=0)
    d_completed = database.Column(database.Integer, name='d_completed', nullable=False, default=0)
    d_edited = database.Column(database.Integer, name='d_edited', nullable=False, default=0)
    compl = database.Column(database.Integer, name='compl', nullable=False, default=0)
    title = database.Column(database.String(250), name='title', nullable=False)
    note = database.Column(database.Text, name='note')
    prio = database.Column(database.Integer, name='prio', nullable=False, default=0)
    ow = database.Column(database.Integer, name='ow', nullable=False, default=0)
    tags = database.Column(database.String(600), name='tags', default='')
    tags_ids = database.Column(database.String(250), name='tags_ids', default='')
    duedate = database.Column(database.Integer, name='duedate', nullable=False, default=0)

    @classmethod
    def max_ow(cls, compl: int = None, list_id: int = None):
        query = database.session.query(func.max(cls.ow))
        if (compl is not None) & (list_id is not None):
            query = query.filter(cls.compl == compl).filter(cls.list_id == list_id)
        return query.first()[0] or 0


class Tags(database.Model):
    __tablename__ = s.values['prefix'] + 'tags'
    id = database.Column(database.Integer, name='id', nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = database.Column(database.String(50), name='name', nullable=False, index=True)


class Tags2Task(database.Model):
    __tablename__ = s.values['prefix'] + 'tags2task'
    id = database.Column(database.Integer, name='id', nullable=False, unique=True, primary_key=True, autoincrement=True)
    tag_id = database.Column(database.Integer, name='tag_id', nullable=False, index=True)
    task_id = database.Column(database.Integer, name='task_id', nullable=False, index=True)
    list_id = database.Column(database.Integer, name='list_id', nullable=False, index=True)

    # def __repr__(self):
    #     return '<tagid %r>' % self.tag_id
