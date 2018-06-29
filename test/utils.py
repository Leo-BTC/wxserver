#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/31 下午5:32
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : utils.py
# @Software: 富融钱通
# @Function: 通用工具类
import logging
import random
import socket
import time
import sys
import traceback
from flask import flash

from test.settings import Config

ISOTIMEFORMAT = '%Y-%m-%d %X'


def flash_errors(form, category='warning'):
    '''
    Flash all errors for a form
    :param form: 表单
    :param category: 类别，此处错误类型
    :return:
    '''
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


class TreeNode:
    def __int__(self, id=None, pid=None, children=None, merchant_code=None):
        """
        树节点信息
        :param id:
        :param pid:
        :param children:
        :return:
        """
        self.id = id
        self.pid = pid
        self.children = children
        self.name = ""
        self.merchant_code = merchant_code

    def dict(self):
        return {'id': self.id, 'name': self.name,
                'children': self.children, 'open': True}


def get_tree_node_by_sys_org(org_list, sys_org):
    """
    获取机构树子集
    :param org_list:
    :param sys_org:
    :return:
    """
    try:
        tree_node_list = []
        tree_node = TreeNode()
        if sys_org:
            tree_node.id = sys_org.org_id
            tree_node.name = sys_org.org_name
            child_list = get_tree_nodes_ds(org_list, sys_org.org_code)
            tree_node.children = child_list
            tree_node_list.append(tree_node.dict())
            return tree_node_list
    except Exception as e:
        raise e


def get_tree_nodes_ds(org_list, pid):
    """
    获取树的子节点
    :param org_list:
    :param pid:
    :return:
    """
    try:
        tree_node_list = []
        for sys_org in org_list:
            org_code = sys_org.org_code
            if pid == org_code:
                pass
            elif pid in org_code:
                tree_node = TreeNode()
                tree_node.id = sys_org.org_id
                tree_node.name = sys_org.org_name
                child_list = get_tree_nodes_ds(org_list, org_code)
                tree_node.children = child_list
                tree_node_list.append(tree_node.dict())
        return tree_node_list
    except Exception as e:
        raise e


def get_current_time():
    """
    获取当前时间点
    :return:
    """
    return time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))


def generate_verification_code():
    """
    随机生成6位数
    :return:
    """
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    myslice = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice)  # list to string
    return verification_code


def import_class(import_str):
    """
    动态引入类
    Returns a class from a string including module and class.
    ersionadded:: 0.3
    :param import_str: 引入类的路径字符串
                       e.g  richwecsweb.sysadmin.forms.OrgForm
    :return:
    """
    logging.info('动态引入FORM表单')
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    try:
        __import__(mod_str)
        return getattr(sys.modules[mod_str], class_str)
    except AttributeError:
        raise ImportError('Class %s cannot be found (%s)' %
                          (class_str,
                           traceback.format_exception(*sys.exc_info())))


def socket_query_param(data):
    """
    向tcp_server 发送报文指令
    data： 指令内容
    :return:
    """
    try:
        param_query = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        param_query.connect((Config.TCP_SERVER_URL, 25000))
        data = str(data).encode('utf-8')
        param_query.send(data)
        revc_data = param_query.recv(1024)
        revc_data = revc_data.decode()
        return eval(revc_data)
    except BaseException as e:
        logging.debug(e)
        return e