#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/26 18:29
# @Author  : linjunjie
# @Site    : www.rich-f.com
# @File    : permission_view.py
# @Software: 富融钱通系统
# @Function: 权限管理功能

import logging
import time
import cgi
from datetime import datetime
from flask_login import login_required
from sqlalchemy import or_, func, and_
from werkzeug.utils import redirect
from flask import Blueprint, request, json, session, render_template, url_for
from test.extensions import csrf_protect, db
from test.responsecode import ResponseCode
from test.sysadmin import message_view
from test.sysadmin.forms import PermissionForm
from test.sysadmin.models import (SysDict, Permissionlist, SysDictType, SysUser, SysUserRole,
                                       SysRolePermissionlist, PermissionType, PermissionStatus)
from test.sysadmin.permission_required import per_required

blueprint = Blueprint('permission', __name__, url_prefix='/permission', static_folder='../static')


@csrf_protect.exempt
@blueprint.route('/', methods=['GET', 'POST'])
@per_required
def permission():
    """
    权限管理主界面
    :return:
    """
    return render_template('sysadmin/syspermission/sys_permission.html', **locals())


@csrf_protect.exempt
@blueprint.route('/get_list', methods=['GET', 'POST'])
@per_required
def permission_get_list():
    """
    获取权限列表
    :return:
    """
    logging.info('permission_get_list')
    try:
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

        dict_data = get_permission_table_data(offset_data, page_size, search_data, sort, sortOrder)
        return json.dumps(dict_data)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '获取失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/disable/<arr>', methods=['GET', 'POST'])
@per_required
def permission_disable(arr):
    """
    停用权限
    :param arr:
    :return:
    """
    logging.info("permission_disable")
    try:
        arr = arr.split(',')
        for i in range(len(arr)):
            id = arr[i]
            disable_the_permission(id)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '操作成功!', 'data': []}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '操作失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/delete/<arr>', methods=['GET', 'POST'])
@per_required
def permission_delete(arr):
    """
    删除权限
    :param arr:
    :return:
    """
    # 权限修改 删除标识
    logging.info("permission_delete")
    try:
        arr = arr.split(',')
        for i in range(len(arr)):
            id = arr[i]
            permission = Permissionlist.query.filter_by(id=id, del_flag=0,).first()  # 获取权限
            if permission:
                if permission.type == 1:
                    name_dict = {'code': ResponseCode.ERROR, 'desc': '操作失败, 默认权限不能删除!', 'data': []}
                    return json.dumps(name_dict)
                delete_the_permission(permission)
            else:
                name_dict = {'code': ResponseCode.ERROR, 'desc': '找不到该权限!', 'data': []}
                return json.dumps(name_dict)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '操作成功!', 'data': []}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '操作失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/usable', methods=['GET', 'POST'])
@per_required
def permission_usable():
    """
    更新权限为可用状态
    :return:
    """
    logging.info('permission_usable')
    try:
        id = request.form.get('id')
        db_permission_usable(id)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '更新状态成功!', 'data': []}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '更新状态失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/add', methods=['GET', 'POST'])
@per_required
def permission_add():
    """
    权限添加页面
    :return:
    """
    logging.info('permission_add')
    permission_form = PermissionForm(request.form)
    permission_form.sort.data = '0'  # 默认排序0

    if permission_form.is_submitted():
        data = request.form
        if permission_form.validate():
            add_permission(data)
            return redirect(url_for('permission.permission'))
    return render_template('sysadmin/syspermission/sys_permission_add.html', **locals())


@csrf_protect.exempt
@blueprint.route('/update/<id>', methods=['GET', 'POST'])
@per_required
def permission_update(id):
    """
    权限更新页面
    :param id:
    :return:
    """
    logging.info('permission_update')
    permission_form = PermissionForm(int(id), request.form)
    permission = get_permission(id)
    old_data = {
        "id": id,
        "name": permission.name,
        'url': permission.url,
        'type': permission.type,
        'status': permission.status,
        'desc': permission.desc,
        'parent_id': permission.parent_id,
        'icon': permission.icon,
        'sort': permission.sort
    }
    permission_form = init_permission_form(permission_form, old_data)

    if permission_form.is_submitted():
        update_data = request.form
        if permission_form.check_update(update_data):
            update_permission(id, update_data)
            return redirect(url_for('permission.permission'))
        else:
            permission_form = init_permission_form(permission_form, update_data)
    return render_template('sysadmin/syspermission/sys_permission_update.html', **locals())


@csrf_protect.exempt
@blueprint.route('/add/get_level_data', methods=['POST'])
@per_required
def permission_add_get_level_data():
    """
    获取权限等级数据
    :return:
    """
    logging.info('permission_add_get_level_data')
    try:
        parent_id = request.values.get('parent_id', default=0, type=int)
        permission_level_data = get_permission_level_data(parent_id)
        data = {'select_data_list': permission_level_data}
        name_dict = {'code': ResponseCode.SUCCESS, 'data': data}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'data': None, 'desc': '获取失败！'}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/update/get_level', methods=['POST'])
@per_required
def permission_get_level():
    """
    获取当前权限全部父级数据
    :return:
    """
    logging.info('permission_get_level')
    try:
        id = request.values.get('id', default=0, type=int)
        permission = get_permission(id)
        if permission:
            json_data = get_permission_level(permission)
            name_dict = {'code': ResponseCode.SUCCESS, 'data': json_data}
            return json.dumps(name_dict)
        else:
            name_dict = {'code': ResponseCode.ERROR, 'data': None, 'desc': '获取失败！'}
            json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'data': None, 'desc': '获取失败！'}
        return json.dumps(name_dict)


class PermissionNode:
    def __int__(self, id=None, parent_id=None, children=None, url=None, icon=None, sort=None):
        self.id = id
        self.parent_id = parent_id
        self.children = children
        self.url = url
        self.name = ''
        self.icon = ''
        self.sort = sort

    def __lt__(self, other):
        return self.sort < other.sort

    def dict(self):
        return {'id': self.id, 'name': self.name, 'url': self.url, 'children': self.children, 'icon': self.icon}


def get_permission_table_data(offset_data, page_size, search_data, sort, sort_order):
    """
    获取权限列表数据
    :param offset_data:
    :param page_size: 页面数量
    :param search_data: 搜索
    :param sort:
    :param sort_order:
    :return:
    """
    logging.info('get_permission_table_data')
    try:
        data = []

        if is_valid_date(search_data):
            all_limit_list = Permissionlist.query.filter(Permissionlist.update_time > search_data + " 00:00:00",
                                                         Permissionlist.update_time < search_data + " 23:59:59")
        else:
            all_limit_list = db.session.query(
                Permissionlist.id, Permissionlist.name, Permissionlist.url,
                Permissionlist.type, Permissionlist.update_time, Permissionlist.sort,
                Permissionlist.status, SysDict.dict_name.label('dict_name'), Permissionlist.icon).filter(or_(
                    Permissionlist.name.like('%' + search_data + '%'),
                    Permissionlist.url.like('%' + search_data + '%'),
                    SysDict.dict_name.like('%' + search_data + '%'),
                    Permissionlist.status.like('%' + is_status(search_data) + '%')
                ), Permissionlist.del_flag == 0,
               SysDict.dict_type == SysDictType.permission_type.value,
               Permissionlist.type == SysDict.dict_id
            ).order_by(sort_in_permission_list(sort, sort_order))

        limit_list = all_limit_list.offset(offset_data).limit(page_size).all()
        permission_type_name_dict = get_name_dict(SysDictType.permission_type.value)  # 权限类型名称字典
        for permission_item in limit_list:
            item = {
                'id': permission_item.id,
                'name': permission_item.name,
                'url': get_html_str(permission_item.url),
                'type': permission_type_name_dict.get(permission_item.type, '空'),
                'update_date': permission_item.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                'status': permission_item.status,
                'sort': permission_item.sort,
                'icon': permission_item.icon
            }
            data.append(item)
        return {'total': len(all_limit_list.all()), 'rows': data}

    except Exception as e:
        logging.debug(e)
        raise e


def sort_in_permission_list(data, sort_order):
    """
    判断排序条件
    :param data:
    :param sort_order:
    :return:
    """
    logging.info('sort_in_permission_list')
    if sort_order == 'asc':
        if data == 'url':
            return db.asc(Permissionlist.url)
        elif data == 'name':
            return db.asc(Permissionlist.name)
        elif data == 'type':
            return db.asc(Permissionlist.type)
        elif data == 'update_date':
            return db.asc(Permissionlist.update_time)
        elif data == 'status':
            return db.asc(Permissionlist.status)
        elif data == 'sort':
            return db.asc(Permissionlist.sort)
        else:
            return db.asc(Permissionlist.sort)
    else:
        if data == 'url':
            return db.desc(Permissionlist.url)
        elif data == 'name':
            return db.desc(Permissionlist.name)
        elif data == 'type':
            return db.desc(Permissionlist.type)
        elif data == 'update_date':
            return db.desc(Permissionlist.update_time)
        elif data == 'status':
            return db.desc(Permissionlist.status)
        elif data == 'sort':
            return db.desc(Permissionlist.sort)
        else:
            return db.desc(Permissionlist.sort)


def get_html_str(text):
    """
    html特殊字符转义
    :param text:
    :return:
    """
    return cgi.escape(text)


def is_status(search_data):
    """
    判断是否有参数，且为正常还是停用
    :param search_data:s
    :return:
    """
    logging.info('is_status')
    if search_data:
        if search_data == '正常':
            return '0'
        elif search_data == '停用':
            return '1'
        else:
            return search_data
    else:
        return ''


def is_valid_date(strdate):
    """
    判断是否是一个有效的日期字符串
    :param strdate:
    :return:
    """
    logging.info('is_valid_date')
    try:
        if ":" in strdate:
            time.strptime(strdate, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(strdate, "%Y-%m-%d")
        return True
    except Exception as e:
        return False


def get_permission_level_data(parent_id):
    """
    获取权限列表等级数据
    :param parent_id:
    :return:
    """
    logging.info('get_permission_level_data')
    try:

        permission_list = Permissionlist.query.filter(Permissionlist.parent_id == parent_id,
                                                      Permissionlist.status == 0,
                                                      Permissionlist.del_flag == 0).\
            order_by(Permissionlist.sort.asc()).all()  # 根据parend_id 查询权限列表
        select_data = list()
        for permission in permission_list:
            item = (permission.id, permission.name)
            select_data.append(item)
        return select_data
    except Exception as e:
        logging.debug(e)
        raise e


def get_permission_level(permission):
    list = []
    list_value = get_parents_data(permission.id, list)
    list_value.reverse()
    list_value.append(permission.id)
    ids_all_list = list_value[1:]
    bTop = permission.parent_id == 0
    result_vale_data = []
    for index, tab_data in enumerate(list_value[0:-1]):
        result_vale_list = []
        select_data_list = []
        val_data = Permissionlist.query.filter_by(parent_id=tab_data, status=0, del_flag=0).all()
        for val_l in val_data:
            if permission.id != val_l.id:
                select_data = []
                select_data.append(val_l.id)
                select_data.append(val_l.name)
                select_data_list.append(select_data)
        result_vale_list.append(select_data_list)
        if bTop:
            result_vale_list.append('-2')
        else:
            result_vale_list.append(ids_all_list[index])

        result_vale_data.append(result_vale_list)

    return result_vale_data


def get_parents_data(id, list):
    logging.info('get_parents_data')
    try:
        parent_id = 0
        if id == 0:
            return list
        else:
            permission = Permissionlist.query.filter_by(id=id, status=0, del_flag=0).first()
            if permission:
                parent_id = permission.parent_id
                list.append(parent_id)
        return get_parents_data(parent_id, list)
    except Exception as e:
        logging.debug(e)
        raise e


def add_permission(data):
    """
    添加权限
    :param data: 添加权限数据 dict类型
    :return:
    """
    logging.info('add_permission')
    parent_id = data.get("parent_id", None)
    url = data.get("url", None)
    name = data.get("name", None)
    permission_type = data.get("type", None)
    status = data.get("status", None)
    desc = data.get("desc", None)
    icon = data.get("icon", None)
    sort = data.get("sort", None)

    db_create_permission(name=name, url=url, permission_type=permission_type,
                         parent_id=parent_id, status=status, icon=icon, desc=desc, sort=sort)  # 数据库新建数据


def get_permission(id):
    """
    通过id获取权限
    :param id:
    :return:
    """
    logging.info('get_permission')
    try:
        return Permissionlist.query.filter_by(id=id, status=0, del_flag=0,).first()
    except Exception as e:
        logging.debug(e)
        raise e


def init_permission_form(form, data):
    """
    初始化表单数据
    :param form:
    :param data:
    :return:
    """
    logging.info('init_permission_form')
    try:
        form.parent_id.data = data.get('parent_id')
        form.name.data = data.get('name')
        form.url.data = data.get('url')
        form.status.data = str(data.get('status'))
        form.type.data = str(data.get('type'))
        form.icon.data = data.get('icon')
        form.desc.data = data.get('desc')
        form.sort.data = data.get('sort')
        return form
    except Exception as e:
        logging.error(e)
        raise e


def update_permission(permission_id, data):
    """
    修改权限
    :param permission_id: 权限id
    :param data: 参数
    :return:
    """
    logging.info('update_permission')
    parent_id = data.get("parent_id", None)
    url = data.get("url", None)
    name = data.get("name", None)
    permission_type = data.get("type", None)
    status = data.get("status", None)
    desc = data.get("desc", None)
    icon = data.get("icon", None)
    sort = data.get("sort", None)

    db_update_permission(permission_id=permission_id, name=name, url=url, permission_type=permission_type,
                         parent_id=parent_id, status=status, icon=icon, desc=desc, sort=sort)  # 数据库新建数据


def get_choices_list(dict_type):
    """
    获取选项列表 类型 list
    :param dict_type: 字典表类型
    :return:
    """
    choices_list = list()
    sys_dict_list = get_sys_dict_list(dict_type)
    for sys_dict in sys_dict_list:
        item = (sys_dict.dict_id, sys_dict.dict_name)
        choices_list.append(item)
    return choices_list


def get_name_dict(dict_type):
    """
    获取字典表名字信息 类型 dict
    :param dict_type: 字典表类型
    :return:
    """
    status_dict = dict()
    sys_dict_list = get_sys_dict_list(dict_type)
    for sys_dict in sys_dict_list:
        item_id = int(sys_dict.dict_id)
        status_dict[item_id] = sys_dict.dict_name
    return status_dict


def get_user_menu(user_id):
    """
    获取用户菜单权限数据
    :param user_id:
    :return:
    """
    logging.info('get_user_menu')
    try:
        if session_user_is_admin():
            # 超级管理员 返回全部菜单
            all_permission_list = db_get_permission_with_type_ignore_status(PermissionType.menu.value)
            tree_list = get_tree_node_by_permission(all_permission_list, 0)
            return tree_list
        user_permission_list = db_get_user_permission_list(user_id, PermissionType.menu.value)
        user_permission_dict = dict()
        for user_permission in user_permission_list:
            user_permission_dict[user_permission.permission_id] = user_permission
        for user_permission in user_permission_list:
            parent_id = int(user_permission.permission_parent_id)
            if parent_id != 0:
                parent_permission = user_permission_dict.get(parent_id, None)
                if parent_permission is None:
                    parent_permission = db_get_permission_with_id(parent_id)
                    if parent_permission:
                        user_permission_dict[parent_permission.permission_id] = parent_permission
                        user_permission_list.append(parent_permission)
        tree_list = get_tree_node_by_permission(user_permission_list, 0)
        return tree_list
    except Exception as e:
        logging.debug(e)
        raise e


def get_user_permission_all_url_list(user_id):
    """
    获取用户全部权限 url list
    :param user_id: 用户id
    :return:
    """
    logging.info('get_user_permission_all_url_list')
    try:
        user_permission_list = db_get_user_permission_all_list(user_id)
        permission_url_list = list()
        for user_permission in user_permission_list:
            permission_url_list.append(user_permission.permission_url)
        return permission_url_list
    except Exception as e:
        logging.debug(e)
        raise e


def get_tree_node_by_permission(permission_list, pid):
    """
    获取用户权限树结构
    :param permission_list:
    :param pid:
    :return:
    """
    try:
        tree_node_list = []
        tree_node_obj_list = []
        for permission in permission_list:
            if permission.permission_parent_id == pid:
                tree_node = PermissionNode()
                tree_node.id = permission.permission_id
                tree_node.name = permission.permission_name
                tree_node.url = permission.permission_url
                tree_node.icon = permission.permission_icon
                tree_node.sort = permission.permission_sort
                child_list = get_tree_node_by_permission(permission_list, permission.permission_id)
                tree_node.children = child_list
                tree_node_obj_list.append(tree_node)
        tree_node_obj_list.sort()
        for tree_node in tree_node_obj_list:
            tree_node_list.append(tree_node.dict())
        return tree_node_list
    except Exception as e:
        logging.debug(e)
        raise e


def get_session_user_name():
    """
    获取session 用户名称
    :return:
    """
    logging.info('get_session_user_name')
    try:
        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        return user.username
    except Exception as e:
        logging.debug(e)
        raise e


def session_user_is_admin():
    """
    检查session 用户是否admin
    :return:
    """
    logging.info('session_user_is_admin')
    try:
        user_id = session.get('user_id', 0)
        user_role = SysUserRole.query.filter_by(user_id=user_id).first()
        if user_role:
            role_id = user_role.role_id
            if role_id == '1':
                return True
            else:
                return False
    except Exception as e:
        logging.debug(e)
        raise e


def disable_the_permission(id):
    """
    停用权限
    :param id:
    :return:
    """
    logging.info('disable_the_permission')
    try:
        user_name = get_session_user_name()
        permission = get_permission(id)
        if permission is not None:
            # 发送操作消息
            message_view.add_option_message("停用权限 '" + permission.name + "'")
            return Permissionlist.update(permission, status=PermissionStatus.disable.value, update_by=user_name,
                                         update_date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    except Exception as e:
        logging.debug(e)
        raise e


def delete_the_permission(permission):
    """
    删除权限 修改权限删除标识
    :param permission:
    :return:
    """
    logging.info('delete_the_permission')
    try:
        user_name = get_session_user_name()
        if permission is not None:
            # 发送操作消息
            message_view.add_option_message("删除权限 '" + permission.name + "'")
            return Permissionlist.update(permission, del_flag=1, update_by=user_name,
                                         update_date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    except Exception as e:
        logging.debug(e)
        raise e


def get_sys_dict_list(dict_type):
    """
    获取权限状态字典表 类型 list
    :param dict_type: 字典表类型
    :return:
    """
    logging.info('get_sys_dict_list')
    try:
        sys_dict_list = SysDict.query.filter_by(dict_type=dict_type, del_flag=0).all()  # 获取字典表权限类型
        return sys_dict_list
    except Exception as e:
        logging.debug(e)
        raise e


def db_update_permission(permission_id, name, url, permission_type, parent_id, status, icon, desc, sort):
    """
    数据库更新权限
    :param permission_id: 权限id
    :param name: 权限名称
    :param url: 权限url
    :param permission_type: 权限类型
    :param parent_id: 父id
    :param status: 权限状态
    :param icon: 图标
    :param desc: 权限描述
    :param sort: 权限排序
    :return:
    """
    logging.info('db_update_permission')
    try:
        create_time = datetime.now()
        user_name = get_session_user_name()
        # 更新权限
        permission = Permissionlist.query.filter_by(id=permission_id).first()
        Permissionlist.update(
            permission, name=name, url=url, type=permission_type, parent_id=parent_id, status=status,
            create_time=create_time, update_time=create_time, create_by=user_name, update_by=user_name,
            icon=icon, desc=desc, sort=sort)
        # 发送操作消息
        message_view.add_option_message("更新权限 '" + name + "' 的信息")
    except Exception as e:
        logging.debug(e)
        raise e


def db_create_permission(name, url, permission_type, parent_id, status, icon, desc, sort):
    """
    数据库创建权限
    :param name: 权限名称
    :param url: 权限url
    :param permission_type: 权限类型
    :param parent_id: 父id
    :param status: 权限状态
    :param icon: 图标
    :param desc: 权限描述
    :param sort: 权限排序
    :return:
    """
    logging.info('db_create_permission')
    try:
        create_time = datetime.now()
        user_name = get_session_user_name()
        # 创建权限
        db.session.add(Permissionlist(name=name, url=url, type=permission_type,
                              parent_id=parent_id, status=status, create_time=create_time,
                              update_time=create_time, create_by=user_name, update_by=user_name,
                              desc=desc, icon=icon, del_flag=0, sort=sort))
        # Permissionlist.create(name=name, url=url, type=permission_type,
        #                       parent_id=parent_id, status=status, create_time=create_time,
        #                       update_time=create_time, create_by=user_name, update_by=user_name,
        #                       desc=desc, icon=icon, del_flag=0, sort=sort)
        db.session.commit()
        # 发送操作消息
        message_view.add_option_message("创建权限 '" + name + "'")
    except Exception as e:
        logging.debug(e)
        raise e


def db_permission_usable(id):
    """
    更新权限为可用状态
    :param id:
    :return:
    """
    logging.info('db_permission_usable')
    try:
        permission = Permissionlist.query.filter_by(id=id).first()
        if permission is not None:
            # 发送操作消息
            message_view.add_option_message("更新权限 '" + permission.name + "' 的状态")
            return Permissionlist.update(permission, status=PermissionStatus.normal.value)
    except Exception as e:
        logging.debug(e)
        raise e


def db_get_user_permission_list(user_id, permission_type=None):
    """
    获取指定权限类型 用户权限列表 类型list
    :param user_id: 用户id
    :param permission_type: 权限类型
    :return:
    """
    logging.info('db_get_user_permission_list')
    try:
        user_role = SysUserRole.query.filter_by(user_id=user_id).first()
        if user_role:
            permission_list = db.session.query(
                Permissionlist.id.label('permission_id'),
                Permissionlist.parent_id.label('permission_parent_id'),
                Permissionlist.name.label('permission_name'),
                Permissionlist.icon.label('permission_icon'),
                Permissionlist.sort.label('permission_sort'),
                Permissionlist.url.label('permission_url')).filter(
                Permissionlist.id == SysRolePermissionlist.permissionlist_id,
                Permissionlist.type == permission_type,
                Permissionlist.status == 0,
                Permissionlist.del_flag == 0,
                SysRolePermissionlist.role_id == user_role.role_id).all()
            return permission_list
        else:
            return []

    except Exception as e:
        logging.debug(e)
        raise e


def db_get_permission_with_id(permission_id):
    logging.info('db_get_permission_with_id')
    try:
        permission = db.session.query(
            Permissionlist.id.label('permission_id'),
            Permissionlist.parent_id.label('permission_parent_id'),
            Permissionlist.name.label('permission_name'),
            Permissionlist.icon.label('permission_icon'),
            Permissionlist.sort.label('permission_sort'),
            Permissionlist.url.label('permission_url')
        ).filter(Permissionlist.id == permission_id, Permissionlist.status == 0, Permissionlist.del_flag == 0).first()
        return permission
    except Exception as e:
        logging.debug(e)
        raise e


def db_get_permission_with_type(permission_type):
    logging.info('db_get_permission_with_type')
    try:
        permission_list = db.session.query(
            Permissionlist.id.label('permission_id'),
            Permissionlist.parent_id.label('permission_parent_id'),
            Permissionlist.name.label('permission_name'),
            Permissionlist.icon.label('permission_icon'),
            Permissionlist.sort.label('permission_sort'),
            Permissionlist.url.label('permission_url')
        ).filter(Permissionlist.type == permission_type,
                 Permissionlist.status == 0,
                 Permissionlist.del_flag == 0).all()
        return permission_list
    except Exception as e:
        logging.debug(e)
        raise e


def db_get_permission_with_type_ignore_status(permission_type):
    """
    根据权限类型获取权限 忽略权限状态
    :param permission_type:权限类型
    :return:
    """
    logging.info('db_get_permission_with_type_ignore_status')
    try:
        if session_user_is_admin():
            permission_list = db.session.query(
                Permissionlist.id.label('permission_id'),
                Permissionlist.parent_id.label('permission_parent_id'),
                Permissionlist.name.label('permission_name'),
                Permissionlist.icon.label('permission_icon'),
                Permissionlist.sort.label('permission_sort'),
                Permissionlist.url.label('permission_url')
            ).filter(Permissionlist.type == permission_type,
                     Permissionlist.del_flag == 0).all()
            return permission_list
        else:
            logging.error('方法调用错误 该方法只能超级管理员调用')
    except Exception as e:
        logging.error(e)
        raise e


def db_get_user_permission_all_list(user_id):
    """
    获取用户所有权限列表 类型list
    :param user_id: 用户id
    :return:
    """
    logging.info('db_get_user_permission_all_list')
    try:
        if session_user_is_admin():
            # 超级管理员 返回全部权限
            return db.session.query(
                Permissionlist.id.label('permission_id'),
                Permissionlist.parent_id.label('permission_parent_id'),
                Permissionlist.sort.label('permission_sort'),
                Permissionlist.name.label('permission_name'),
                Permissionlist.url.label('permission_url')).filter(Permissionlist.del_flag == 0).all()
        # 添加默认权限
        permission_list = list()
        default_permission_list = db_get_permission_with_type(PermissionType.default.value)
        permission_list.extend(default_permission_list)

        # 添加用户拥有权限
        user_role = SysUserRole.query.filter_by(user_id=user_id).first()
        if user_role:
            user_permission_list = db.session.query(
                Permissionlist.id.label('permission_id'),
                Permissionlist.parent_id.label('permission_parent_id'),
                Permissionlist.sort.label('permission_sort'),
                Permissionlist.name.label('permission_name'),
                Permissionlist.url.label('permission_url')).filter(
                Permissionlist.id == SysRolePermissionlist.permissionlist_id,
                Permissionlist.status == 0,
                Permissionlist.del_flag == 0,
                SysRolePermissionlist.role_id == user_role.role_id).all()
            if user_permission_list:
                permission_list.extend(user_permission_list)
        return permission_list

    except Exception as e:
        logging.debug(e)
        return []
