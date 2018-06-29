#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午6:07
# @Author  : Lee才晓
# @Site    : www.rich-f.com
# @File    : dict_view.py
# @Software: 富融钱通
# @Function: 字典模块逻辑操作
import io
import time
import xlrd
import xlwt
import logging
from flask import Blueprint, render_template, request, json, make_response, url_for, session
from gevent import os
from sqlalchemy import or_
from werkzeug.utils import secure_filename, redirect
from test.extensions import db, csrf_protect
from test.responsecode import ResponseCode
from test.sysadmin import message_view
from test.sysadmin.forms import DictForm
from test.sysadmin.models import SysDict, SysUser, SysOrg
from test.sysadmin.permission_required import per_required
from test.utils import flash_errors

blueprint = Blueprint('sysdict', __name__, url_prefix='/sysdict', static_folder='../static')
ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])
DictKeys = ['字典名',
            '字典id号',
            '字典类型',
            '描述',
            '序号',
            '创建者',
            '创建时间',
            '更新者',
            '更新时间',
            '备注',
            '删除标志']


###########路由地址区域####################

@blueprint.route('/', methods=['GET'])
@per_required
def dict():
    """
    字典表主界面
    :return:
    """
    logging.info('dict')
    return render_template('sysadmin/sysdict/sys_dict.html', **locals())

@csrf_protect.exempt
@blueprint.route('/dict_add', methods=['GET', 'POST'])
@per_required
def dict_add():
    """
    字典添加界面
    :return:
    """
    logging.info('dict_add')
    try:
        dict_form = DictForm(request.form)

        if dict_form.is_submitted():
            data = request.form
            if dict_form.validate('add', None, data):

                add_dict(data)
                return redirect(url_for('sysdict.dict'))
            else:
                flash_errors(dict_form)
        return render_template('sysadmin/sysdict/sys_dict_add.html', **locals())
    except Exception as e:
        logging.debug(e)
        raise e


@csrf_protect.exempt
@blueprint.route('/dict_update/<id>', methods=['GET', 'POST'])
@per_required
def dict_update(id):
    """
    字典更新界面
    :param id:
    :return:
    """
    logging.info('dict_update')
    try:
        dict_form = DictForm(request.form)
        old_data = {}
        dict = get_the_dict_by_id(id)
        old_data['id'] = id
        old_data['dict_name'] = dict.dict_name
        old_data['dict_id'] = dict.dict_id
        old_data['dict_type'] = dict.dict_type
        old_data['description'] = dict.description
        old_data['sort'] = dict.sort
        old_data['del_flag'] = dict.del_flag
        old_data['remarks'] = dict.remarks
        dict_form = init_view(dict_form, old_data)

        if dict_form.is_submitted():
            new_data = request.form
            if dict_form.validate('update', old_data, new_data):

                update_dict(id, new_data)
                return redirect(url_for('sysdict.dict'))
            else:
                flash_errors(dict_form)
        return render_template('sysadmin/sysdict/sys_dict_update.html', dict_form=dict_form, dict=old_data)
    except Exception as e:
        logging.debug(e)
        raise e


@csrf_protect.exempt
@blueprint.route('/dict_delete/<arr>', methods=['GET', 'POST'])
@per_required
def dict_delete(arr):
    """
    删除字典
    :param id:
    :return:
    """
    logging.info("dict_delete")

    try:
        arr = arr.split(',')
        for i in range(len(arr)):
            id = arr[i]
            delete_the_dict(id)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '删除成功!', 'data': []}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '删除失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/dict/get_list', methods=['GET', 'POST'])
@per_required
def dict_get_list():
    """
    获取字典列表
    :return:
    """
    logging.info('dict_get_list')
    try:
        offset_data = 0
        page_number = request.args.get('pageNumber')
        page_size = request.args.get('pageSize')
        search_data = request.args.get('searchData')
        sort = request.args.get('sort')
        sortOrder = request.args.get('sortOrder')
        if search_data:
            offset_data = int(page_number)
        else:
            search_data = ''
            offset_data = int(page_number)

        dict_data = get_dict_all_limit(offset_data, page_size, search_data, sort, sortOrder)
        return json.dumps(dict_data)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '获取失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/dict_export', methods=['GET', 'POST'])
@per_required
def dict_export():
    """
    导出文件
    :return:
    """
    try:
        logging.info('dict_export')

        dict_data = get_dict_all()

        io = export_excel(dict_data)

        message_view.add_option_message("尝试导出字典文件")

        response = make_response(io)
        response.headers['Content-Type'] = 'application/vnd.ms-excel'
        response.headers["Content-Disposition"] = "attachment; filename=sys_dict.xls;"
        return response
    except Exception as e:
        logging.debug(e)
        return None


@csrf_protect.exempt
@blueprint.route('/dict_import', methods=['GET', 'POST'])
@per_required
def dict_import():
    """
    导入文件
    :return:
    """
    try:
        logging.info('dict_import')
        name_dict = {}
        file = request.files['file']
        file_path = import_excel(file)
        if file_path == '-1':
            name_dict = {'code': ResponseCode.ERROR, 'desc': '文件格式不匹配!', 'data': []}

        else:
            if read_excel(file_path) == -1:
                name_dict = {'code': ResponseCode.ERROR, 'desc': '文件内容不匹配!', 'data': []}
            else:
                message_view.add_option_message("导入字典文件")
                name_dict = {'code': ResponseCode.SUCCESS, 'desc': '文件上传成功!', 'data': []}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '文件上传失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/dict_update_del_flag', methods=['POST'])
@per_required
def dict_update_del_flag():
    """
    恢复正常状态
    :return:
    """
    try:
        logging.info('dict_update_del_flag')
        id = request.form.get('id')
        update_del_flag(id)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '更新状态成功!', 'data': []}
        return json.dumps(name_dict)

    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '更新状态失败!', 'data': []}
        return json.dumps(name_dict)


################路由地址区域结束############################


################业务逻辑区域############################
def update_del_flag(id):
    """
    标记是否删除
    :param id:
    :return:
    """
    logging.info('update_del_flag')
    try:
        dict = SysDict.query.filter_by(id=id).first()
        if dict is not None:
            dict = SysDict.update(dict, del_flag=0)
            if dict:
                message_view.add_option_message("恢复字典 '"+dict.dict_name+"'")
    except Exception as e:
        logging.debug(e)
        raise e


def get_dict_all():
    """
    获取所有的字典数据
    :return:
    """
    logging.info('get_dict_all')
    try:
        data = []
        all_dict = SysDict.query.all()
        ##SysDict.query.all()
        for dict in all_dict:
            item = {}
            item['id'] = dict.id
            item['dict_name'] = dict.dict_name
            item['dict_id'] = dict.dict_id
            item['dict_type'] = dict.dict_type
            item['description'] = dict.description
            item['sort'] = dict.sort
            item['remarks'] = dict.remarks
            item['del_flag'] = dict.del_flag
            item['create_by'] = dict.create_by
            item['create_time'] = dict.create_time
            item['update_by'] = dict.update_by
            item['update_time'] = dict.update_time
            data.append(item)

        return data
    except Exception as e:
        logging.debug(e)
        raise e


def get_dict_all_limit(offset_data, page_size, search_data, sort, sortOrder):
    """
    获取所有的字典数据
    :return:
    """
    logging.info('get_dict_all_limit')
    try:
        data = []

        all_limit_dict = SysDict.query.filter(or_(SysDict.dict_name.like('%'+search_data + '%'),
                                                  SysDict.dict_id.like('%'+search_data + '%'),
                                                  SysDict.dict_type.like('%'+search_data + '%'),
                                                  SysDict.description.like('%'+search_data + '%'),
                                                  SysDict.sort.like('%'+search_data + '%'),
                                                  SysDict.remarks.like('%'+search_data + '%'))
                                              ).order_by(sort_in_sysuser(sort, sortOrder))
        limit_dict = all_limit_dict.offset(offset_data).limit(page_size).all()
        for dict in limit_dict:
            item = {}
            item['sort'] = dict.sort
            item['dict_name'] = dict.dict_name
            item['dict_id'] = dict.dict_id
            item['dict_type'] = dict.dict_type
            item['description'] = dict.description
            item['remarks'] = dict.remarks
            item['del_flag'] = dict.del_flag
            item['create_by'] = dict.create_by
            item['create_time'] = dict.create_time
            item['update_by'] = dict.update_by
            item['update_time'] = dict.update_time
            item['id'] = dict.id
            data.append(item)

        return {'total': all_limit_dict.count(), 'rows': data}
    except Exception as e:
        logging.debug(e)
        raise e


def sort_in_sysuser(data, sortOrder):
    """
    判断排序条件
    :param data:
    :param sortOrder:
    :return:
    """
    logging.info('sort_in_sysuser')
    if sortOrder == 'asc':
        if data == 'sort':
            return SysDict.sort.asc()
        elif data == 'dict_name':
            return SysDict.dict_name.asc()
        elif data == 'dict_id':
            return SysDict.dict_id.asc()
        elif data == 'dict_type':
            return SysDict.dict_type.asc()
        elif data == 'description':
            return SysDict.description.asc()
        elif data == 'remarks':
            return SysDict.remarks.asc()
        elif data == 'del_flag':
            return SysDict.del_flag.asc()
        else:
            return None
    else:
        if data == 'sort':
            return SysDict.sort.desc()
        elif data == 'dict_name':
            return SysDict.dict_name.desc()
        elif data == 'dict_id':
            return SysDict.dict_id.desc()
        elif data == 'dict_type':
            return SysDict.dict_type.desc()
        elif data == 'description':
            return SysDict.description.desc()
        elif data == 'remarks':
            return SysDict.remarks.desc()
        elif data == 'del_flag':
            return SysDict.del_flag.desc()
        else:
            return None


def add_dict(data):
    """
    新增字典
    :param data:
    :return:
    """
    logging.info('add_dict')
    try:
        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        # dict = SysDict.create(dict_name=data['dict_name'], dict_type=data['dict_type'], description=data['description'],
        #                       remarks=data['remarks'], dict_id=data['dict_id'], create_by=user.username,
        #                       update_by=user.username, sort=data['sort'], del_flag=int(data['del_flag']))
        db.session.add(SysDict(dict_name=data['dict_name'], dict_type=data['dict_type'], description=data['description'],
                              remarks=data['remarks'], dict_id=data['dict_id'], create_by=user.username,
                              update_by=user.username, sort=data['sort'], del_flag=int(data['del_flag'])))
        db.session.commit()
        if dict:
            message_view.add_option_message("新增字典 '" + data['dict_name'] + "'")

    except Exception as e:
        logging.debug(e)
        raise e


def get_the_dict(dict_id):
    """
    通过dict_id获取字典
    :param dict_id:
    :return:
    """
    logging.info('get_the_dict')
    try:
        return SysDict.query.filter_by(dict_id=dict_id).first()
    except Exception as e:
        logging.debug(e)
        raise e


def get_the_dict_by_id(id):
    """
    通过id获取字典
    :param id:
    :return:
    """
    logging.info('get_the_dict_by_id')
    try:
        return SysDict.query.filter_by(id=id).first()
    except Exception as e:
        logging.debug(e)
        raise e


def update_dict(id, data):
    """
    更新字典
    :param id:
    :param data:
    :return:
    """
    logging.info('update_dict')
    try:
        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        dict = get_the_dict_by_id(id)
        if dict is not None:
            dict = SysDict.update(dict, dict_name=data['dict_name'], dict_id=data['dict_id'],
                                  dict_type=data['dict_type'], sort=data['sort'], del_flag=int(data['del_flag']),
                                  description=data['description'], remarks=data['remarks'], update_by=user.username,
                                  update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            if dict:
                message_view.add_option_message("更新字典 '" + data['dict_name'] + "'")

    except Exception as e:
        logging.debug(e)
        raise e


def delete_the_dict(id):
    """
    更改字典的删除标志
    :param id:
    :return:
    """
    logging.info('delete_the_dict')
    try:
        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        dict = get_the_dict_by_id(id)
        if dict is not None:
            dict = SysDict.update(dict, del_flag=1, update_by=user.username,
                                  update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            if dict:
                message_view.add_option_message("停用字典 '" + dict.dict_name + "'")

    except Exception as e:
        logging.debug(e)
        raise e


def export_excel(dict_data):
    """
    导出excel
    :param dict_data: 字节流
    :return:
    """
    logging.info('export_excel')
    try:
        wb = xlwt.Workbook(encoding='utf-8')
        sheet = wb.add_sheet(u'字典表')
        # 1st line
        for i in range(len(DictKeys)):
            sheet.write(0, i, DictKeys[i])

        row = 1
        for i in range(len(dict_data)):
            sheet.write(row, 0, dict_data[i].get('dict_name'))
            sheet.write(row, 1, dict_data[i].get('dict_id'))
            sheet.write(row, 2, dict_data[i].get('dict_type'))
            sheet.write(row, 3, dict_data[i].get('description'))
            sheet.write(row, 4, dict_data[i].get('sort'))
            sheet.write(row, 5, dict_data[i].get('create_by'))
            sheet.write(row, 6, str(dict_data[i].get('create_time')))
            sheet.write(row, 7, dict_data[i].get('update_by'))
            sheet.write(row, 8, str(dict_data[i].get('update_time')))
            sheet.write(row, 9, dict_data[i].get('remarks'))
            sheet.write(row, 10, dict_data[i].get('del_flag'))

            row += 1

        # wb.save('log.xls')#保存临时文件
        sio = io.BytesIO()
        wb.save(sio)  # 字节流保存
        return sio.getvalue()

    except Exception as e:
        logging.debug(e)
        raise e


def allowed_file(filename):
    """
    判断文件后缀
    :param filename:
    :return:
    """
    logging.info('allowed_file')
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def import_excel(file):
    """
    上传文件
    :param file:
    :return:
    """
    logging.info('import_excel')
    try:
        if allowed_file(file.filename):

            filename = secure_filename(file.filename)
            user_id = session.get('user_id', 0)
            user = SysUser.query.filter_by(id=user_id).first()

            temporary_file = user.username + "-" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            basepath = os.path.dirname(__file__)  # 当前文件所在路径
            import platform
            CURRENT_SYSTEM = platform.system()
            if CURRENT_SYSTEM == 'Windows':
                current_path = '\\static\\temporary\\dict_files\\'
            else:
                current_path = '/static/temporary/dict_files'
            upload_path = os.path.join(basepath, current_path,
                                       secure_filename(temporary_file))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
            file.save(upload_path)
            return upload_path
        else:
            return '-1'
    except Exception as e:
        logging.debug(e)
        raise e


def read_excel(file_path):
    """
    读取excel文件
    :param file_path: 文件路径
    :return:
    """
    logging.info('read_excel')
    try:
        data = xlrd.open_workbook(file_path)

        Sheets = data.sheets()  # 获取工作表list。

        the_Sheet = Sheets[0]  # 获取工作表
        nrows = the_Sheet.nrows  # 行数
        ncols = the_Sheet.ncols  # 列数

        if not is_eligible_files(ncols, the_Sheet.row_values(0)):
            return -1

        for i in range(1, nrows):
            dict = SysDict()
            dict.dict_name = the_Sheet.row_values(i)[0]
            dict.dict_id = the_Sheet.row_values(i)[1]
            dict.dict_type = the_Sheet.row_values(i)[2]
            dict.description = the_Sheet.row_values(i)[3]
            dict.sort = the_Sheet.row_values(i)[4]
            dict.create_by = the_Sheet.row_values(i)[5]
            dict.create_time = the_Sheet.row_values(i)[6]
            dict.update_by = the_Sheet.row_values(i)[7]
            dict.update_time = the_Sheet.row_values(i)[8]
            dict.remarks = the_Sheet.row_values(i)[9]
            dict.del_flag = the_Sheet.row_values(i)[10]

            old_dict = SysDict.query.filter(SysDict.dict_name == dict.dict_name,
                                            SysDict.dict_type == dict.dict_type).first()
            if old_dict is not None:
                SysDict.delete(old_dict)

            db.session.add(dict)

        db.session.commit()
        db.session.close()

        # 删除临时文件
        # if os.path.isfile(file_path):
        #     os.remove(file_path)
        return 0
    except Exception as e:
        logging.debug(e)
        raise e


def isExist(dict_name, dict_type):
    """
    判断该字典是否存在
    :param dict_name:
    :param dict_type:
    :return:
    """
    logging.info('isExist')
    try:
        dict = SysDict.query.filter(dict_name == dict_name).filter(dict_type == dict_type).first()
        if dict is not None:
            return True
        return False
    except Exception as e:
        logging.debug(e)
        raise e


def is_eligible_files(length, data):
    """
    判断文件内容是否符合
    :return:
    """
    logging.info('is_eligible_files')
    if length != len(DictKeys):
        return False
    for i in range(len(DictKeys)):
        if data[i] != DictKeys[i]:
            return False
    return True


def init_view(form, data):
    """
       初始化表单数据
       :param obj:
       :param dict:
       :return:
       """
    logging.info('init_view')
    try:
        form.dict_name.data = data.get('dict_name')
        form.dict_id.data = data.get('dict_id')
        form.dict_type.data = data.get('dict_type')
        form.description.data = data.get('description')
        form.sort.data = data.get('sort')
        form.del_flag.data = str(data.get('del_flag'))
        form.remarks.data = data.get('remarks')
        return form
    except Exception as e:
        logging.debug(e)
        raise e

################业务逻辑区域结束############################
