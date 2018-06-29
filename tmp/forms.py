#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/22 16:56
# @Author  : WangYingqi
# @Site    : 
# @File    : forms.py
# @Software: PyCharm
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms import StringField, SelectField

class ztestForm(Form):
    """表单"""
    col

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(ztestForm, self).__init__(*args, **kwargs)
        choices()

    def validate(self, new_data):
        super(ztestForm, self).validate()
        isError = True

        val()

        if not isError:
            return isError

        return isError

    def validate_float(self, number):
        # 校验输入的字符串是否为浮点数
        try:
            float(number)
            return True
        except:
            return False

    def validate_integer(self, number):
        # 校验输入的字符串是否为整型
        try:
            int(number)
            return True
        except:
            return False
        
