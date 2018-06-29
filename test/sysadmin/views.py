#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/26 18:29
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : permission_view.py
# @Software: 富融钱通系统
# @Function: sysadmin模块

import logging
from flask import Blueprint, render_template
from flask_login import login_required
from test.sysadmin.permission_view import get_user_menu


blueprint = Blueprint('sysadmin', __name__, url_prefix='/sysadmin', static_folder='../static')


@blueprint.route('/index')
@login_required
def home():
    logging.info('home')
    # return render_template('gooledemo.html')
    return render_template('index.html', **locals())


