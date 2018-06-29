#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午3:53
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : extensions.py
# @Software: 富融钱通
# @Function: flask外部插件管理


import types

from flask_celery import Celery
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_json import FlaskJSON
from flask_logconfig import LogConfig
from flask_socketio import SocketIO

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
debug_toolbar = DebugToolbarExtension()
marshmallow = Marshmallow()  # http://marshmallow-sqlalchemy.readthedocs.io/en/latest/ 使用文档说明
api = Api(decorators=[csrf_protect.exempt])  # csrf
json = FlaskJSON()  # JSON
logcfg = LogConfig()  # LOG
socket_io = SocketIO()  # sockt_io
mail = Mail()
celery = Celery()  # 异步任务系统


def api_route(self, *args, **kwargs):
    """
        api_route
    """

    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls

    return wrapper


api.route = types.MethodType(api_route, api)

login_manager.session_protection = 'strong'
login_manager.login_view = 'public.login'

