#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/16 15:00
# @Author  : liuzhi
# @File    : views.py
# @Software: 井电双控

import logging
from flask import Blueprint, render_template, session, request
from flask_login import login_required
from test.sysadmin.models import SysOrg, SysDict
from test.extensions import db
from sqlalchemy import or_
import json

blueprint = Blueprint('index', __name__, url_prefix='/index', static_folder='../static')


@blueprint.route('/home/')
@login_required
def home():
    logging.info('home')
    return render_template('index.html')

