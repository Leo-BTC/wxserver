#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/31 下午2:34
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : forms.py
# @Software: 富融钱通
# @Function: 登录表单

import logging
from flask_wtf import Form
from sqlalchemy import or_

from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired
from test.sysadmin.models import SysUser


class LoginForm(Form):
    '''
    登录表单
    '''

    username = StringField('Username', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('Password',
                             validators=[DataRequired(message='密码不能为空')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None
        self.org_id = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = SysUser.query.filter(or_(SysUser.username == self.username.data,
                                             SysUser.chat_code == self.username.data,
                                             SysUser.mobile == self.username.data,
                                             SysUser.email == self.username.data)
                                         ).first()

        if not self.user:
            self.username.errors.append('该用户未注册！')
            logging.info('该用户未注册！')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('密码错误！')
            logging.info('密码错误！')
            return False

        if self.user.is_active == 0:
            self.username.errors.append('该用户已停用')
            return False
        return True
