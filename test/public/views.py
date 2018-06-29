#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午6:07
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : views.py
# @Software: 富融钱通
# @Function: 公共网页入口
import requests
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_user, logout_user
from test.extensions import csrf_protect, login_manager,  db

from test.sysadmin.models import SysUser, SysOrg
from test.sysadmin import permission_view
from test.sysadmin.permission_required import per_required
from test.utils import flash_errors, get_current_time
from .forms import LoginForm
import logging

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    logging.info('load_user')
    return SysUser.get_by_id(int(user_id))


@csrf_protect.exempt
@blueprint.route('/index', methods=['GET', 'POST'])
@blueprint.route('/', methods=['GET', 'POST'])
def home():
    logging.info('home')
    return render_template('public/home.html')


@csrf_protect.exempt
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    logging.info('login')
    login_form = LoginForm(request.form)
    if login_form.validate_on_submit():
        login_user(login_form.user)
        session['user_id'] = login_form.user.id
        session['user_name'] = login_form.user.username
        session['menu'] = permission_view.get_user_menu(login_form.user.id)
        # session['user_permission_list'] = permission_view.get_user_permission_all_url_list(login_form.user.id)
        user = SysUser.query.filter_by(id=session['user_id']).first()
        session['last_login'] = user.last_login
        SysUser.update(
            user,
            last_login=get_current_time()
        )
        if user.avatar == None:
            session['avatar'] = 'default.png'
        else:
            session['avatar'] = user.avatar
        org = SysOrg.query.filter_by(org_id=user.org_id).first()
        session['org_code'] = org.org_code
        session['province'] = org.org_area[:2] + '0000' if org.org_area else '110000'
        return redirect(url_for('index.home'))
    else:
        flash_errors(login_form)

    return render_template(session.get('loggin_content', 'login.html'), **locals())


@blueprint.route("/logout/")
@per_required
def logout():
    login_form = LoginForm(request.form)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('menu', None)
    session.pop('user_permission_list', None)
    session.pop('last_login', None)
    session.pop('avatar', None)
    session.pop('org_code', None)
    session.pop('merchant_code', None)

    logout_user()
    return redirect(url_for('public.login'))


