#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午3:51
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : compat.py
# @Software: 富融钱通
# @Function: PY2和PY3字符集管理

import sys

PY2 = int(sys.version[0]) == 2

if PY2:
    text_type = 'utf-8'  # noqa
    binary_type = str
    string_types = (str, 'utf-8')  # noqa
    unicode = 'utf-8'  # noqa
    basestring = 'utf-8'  # noqa
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    unicode = str
    basestring = (str, bytes)
