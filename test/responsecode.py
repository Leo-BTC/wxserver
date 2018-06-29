#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午4:24
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : responsecode.py
# @Software: 富融钱通
# @Function: 响应状态码


class ResponseCode(object):

    SUCCESS = "0"
    ERROR = "-1"
    PARAMETER_ERROR = '-2'
    PERMISSIONERROR = '-3'

    def __init__(self):
        # super().__init__()
        self.result = {}
        self.result['0'] = '请求成功'
        self.result['-1'] = '请求失败'
        self.result['-2'] = '请求参数错误'
        self.result['-3'] = '没有权限'
    def get_code(self, code):
        return self.result[code]
