#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午3:36
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : start.py
# @Software: Rich_WECS_Web
# @Function: 启动入口


from flask.helpers import get_debug_flag
from test.app import create_app, socket_io
# from test.extensions import celery
from test.settings import DevConfig, ProdConfig
from flask_script import Manager


CONFIG = DevConfig if get_debug_flag() else ProdConfig
app = create_app(CONFIG)
# celery.conf.update(app.config)
# celery.init_app(app)
manager = Manager(app)


@manager.command
def run():
    socket_io.run(app, host='0.0.0.0', port=8888)
if __name__ == '__main__':
    manager.run()
