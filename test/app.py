#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午3:36
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : app.py
# @Software: 富融钱通平台
# @Function: 主程序入口

from flask import Flask, render_template
from .assets import env
from . import (public, sysadmin, index)
from . import apis
# from test  import (mol())
from .extensions import (
    bcrypt, csrf_protect, db,
    debug_toolbar, login_manager,
    marshmallow, api, json, logcfg, socket_io, mail
)


def create_app(config_object):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    flask_name = __name__.split('.')[0]
    app = Flask(flask_name)
    app.config.from_object(config_object)
    set_mail(app)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    env.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    marshmallow.init_app(app)
    json.init_app(app)  # json 格式化
    logcfg.init_app(app)  # log配置信息
    socket_io.init_app(app)
    mail.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    # public  登陆模块
    app.register_blueprint(public.views.blueprint)

    # sysadmin  系统管理 + 信息中心
    app.register_blueprint(sysadmin.views.blueprint)
    app.register_blueprint(sysadmin.org_view.blueprint)
    app.register_blueprint(sysadmin.permission_view.blueprint)
    app.register_blueprint(sysadmin.user_view.blueprint)
    app.register_blueprint(sysadmin.dict_view.blueprint)
    app.register_blueprint(sysadmin.role_view.blueprint)
    app.register_blueprint(sysadmin.message_view.blueprint)
    app.register_blueprint(apis.views.blueprint)
    # appcon()

    # index  首页
    app.register_blueprint(index.index_views.blueprint)

    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def set_mail(app):
    '''

    :param app:
    :return:
    '''
    app.config['MAIL_SERVER'] = 'smtp.exmail.qq.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'service@rich-f.com'
    app.config['MAIL_PASSWORD'] = 'Rich1888'

    return None
