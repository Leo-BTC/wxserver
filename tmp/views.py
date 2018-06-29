#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/18 14:02
# @Author  : WangYingqi
# @Site    : 
# @File    : views.py
# @Software: PyCharm

from werkzeug.utils import redirect
import logging
from flask import Blueprint, request, render_template, url_for, json
from sqlalchemy import or_
from test.extensions import csrf_protect
from db_name import jcre
from test.file_path.forms import jcreForm

blueprint = Blueprint('ztest', __name__, url_prefix='/ztest', static_folder='../static')


@csrf_protect.exempt
@blueprint.route('/', methods=['GET', 'POST'])
def views():
    """
    主界面
    """
    return render_template('ztest/ztest.html', **locals())


@csrf_protect.exempt
@blueprint.route('/get/list')
def get_list():
    """
    database加载的列表
    :return:
    """
    logging.info('get_list')
    try:
        search_data = request.args.get('searchData')
        logging.info('search_data:%s' + str(search_data))
        if search_data:
            pass
        else:
            search_data = ''
        res_data, list_count = get_list_by_user(search_data)
        req_data = {'total': list_count, 'rows': res_data}
        return json.dumps(req_data)
    except Exception as e:
        logging.exception(e)
        return json.dumps({'total': 0, 'rows': []})


def get_list_by_user(search_data):
    """
    获取列表
    :param :
    :return:
    """
    logging.info('get_list_by_user')
    try:
        res_data = []
        listdata = jcre.query.filter(
            or_()
        )
        len = listdata.count()
        for item in listdata:
            dict = {}
            dicts
            res_data.append(dict)
        return res_data, len
    except Exception as e:
        logging.debug(e)
        raise e

def get_list_data(data):
    """
    对表单数据处理
    :param :
    :return:
    """
    if data:
        pass
    else:
        data = ''
    if type(data) == type(True):
        data = int(data)
    return str(data)


@csrf_protect.exempt
@blueprint.route('/add/', methods=['GET', 'POST'])
def add():
    """
    新增数据
    """
    logging.info('add')
    try:
        form = jcreForm(request.form)
        if form.is_submitted():
            data = request.form
            if form.validate(data):
                cre()
                return redirect(url_for('ztest.views'))
        return render_template('ztest/add.html', **locals())
    except Exception as e:
        logging.debug(e)
        raise e


@csrf_protect.exempt
@blueprint.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    """
    编辑数据
    """
    logging.info('edit')
    try:
        form = jcreForm(request.form)
        old_data = {}
        ZTEST = jcre.query.get(int(id))
        dit()
        ztest_form = init_view(form, old_data)
        if ztest_form.is_submitted():
            new_data = request.form
            if form.validate(new_data):
                upt()
                return redirect(url_for('ztest.views'))
        return render_template('ztest/edit.html', **locals())
    except Exception as e:
        logging.debug(e)
        raise e


@csrf_protect.exempt
@blueprint.route('/delete/<arr>', methods=['GET', 'POST'])
def delete(arr):
    """
    删除数据
    """
    logging.info('delete')
    try:
        arr = arr.split(',')
        for i in range(len(arr)):
            id = arr[i]
            jcre.query.get(int(id)).delete()
        name_dict = {'code': '00', 'desc': '删除成功!'}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        raise e


def init_view(form, data):
    """
       编辑时初始化表单数据
       :param obj:
       :param dict:
       :return:
       """
    logging.info('init_view')
    try:
        form_d()
        return form
    except Exception as e:
        logging.debug(e)
        raise e
