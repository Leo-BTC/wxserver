#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午4:15
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : encoder.py
# @Software: 富融钱通
# @Function: 自定义sqlalchemy转码Encoder

import json
from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(json.JSONEncoder):
    """
     json alchemy Qiailin
     转换 orm models class
    """

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:  # 排除 metadata
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data, ensure_ascii=False)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)