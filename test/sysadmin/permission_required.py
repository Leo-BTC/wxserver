#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/26 18:29
# @Author  : linjunjie
# @Site    : www.rich-f.com
# @File    : permission_required.py
# @Software: 富融钱通系统
# @Function: 权限验证模块

import logging
from functools import wraps
from flask_login import current_user, login_required
from flask import request, render_template, jsonify
from test.responsecode import ResponseCode

def permission_required():
    """
    验证用户权限
    """
    logging.info('permission_required')

    def decorator(f):
        @wraps(f)
        @login_required  # 验证用户登录
        def decorated_function(*args, **kwargs):
            url_rule = request.url_rule.rule  # 获取当前请求url路径
            if not current_user.can(url_rule):  # 当前用户是否有权限
                if request.is_xhr:
                    name_dict = {'code': ResponseCode.PERMISSIONERROR,
                                 'desc': "没有权限",
                                 'msg': "没有权限"}
                    return jsonify(name_dict)
                else:
                    return render_template('403.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def per_required(f):
    """
    权限验证装饰器
    :param f:
    :return:
    """
    logging.info('per_required')
    return permission_required()(f)
