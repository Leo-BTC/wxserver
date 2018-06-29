#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午4:48
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : log.py
# @Software: 富融钱通
# @Function: 日志处理模块
# 参考https://github.com/dgilland/flask-logconfig/blob/master/tests/test_flask_logconfig.py



import logging
from pprint import pformat
from flask import request

from flask_logconfig import request_context_from_record


class RequestFilter(logging.Filter):
    """Impart contextual information related to Flask HTTP request."""

    def filter(self, record):
        """Attach request contextual information to log record."""

        with request_context_from_record(record):
            # logging.debug("RequestFilter.......")
            record.environ_info = request.environ.copy()
            record.environ_text = pformat(record.environ_info)
        return True
