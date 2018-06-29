#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/1 15:29
# @Author  :  黄平
# @Site    : www.rich-f.com
# @File    : role_view.py
# @Software: 富融钱通系统
# @Function: 角色管理功能


import logging
from flask import url_for
from flask import Blueprint, render_template, session, request, json, redirect
from test.extensions import csrf_protect, db
from test.responsecode import ResponseCode
from test.sysadmin import message_view
from test.sysadmin.forms import RoleForm
from test.sysadmin.models import Permissionlist, Rolelist, SysRolePermissionlist, SysUser, SysOrg, SysUserRole
from test.sysadmin.permission_required import per_required
from sqlalchemy import not_, or_, desc, func
from datetime import datetime
from test.sysadmin.permission_view import session_user_is_admin

blueprint = Blueprint('sysrole', __name__, url_prefix='/sysrole', static_folder='../static')


@blueprint.route('/role/get/list')
@per_required
def role_get_list():
    """
    database加载的当前机构下角色列表
    :return:
    """
    logging.info('role_get_list')
    try:
        id = session.get("user_id", 0)
        page_number = request.args.get('pageNumber')
        page_size = request.args.get('pageSize')
        offset_data = (int(page_number))
        search_data = request.args.get('searchData')
        sort = request.args.get('sort')
        sortOrder = request.args.get('sortreOrder')
        logging.info('search_data:%s' + str(search_data))
        if search_data:
            offset_data = int(page_number)
        else:
            search_data = ''
            offset_data = int(page_number)
        res_data, list_count = get_role_list_by_user(id, offset_data, page_size, search_data, sort, sortOrder)
        req_data = {'total': list_count, 'rows': res_data}
        return json.dumps(req_data)
    except Exception as e:
        logging.exception(e)
        return json.dumps({'total': 0, 'rows': []})


@blueprint.route('/role')
@per_required
def role():
    logging.info('role')
    return render_template('sysadmin/sysrole/sys_role.html')


@csrf_protect.exempt
@blueprint.route('/role/add', methods=['GET', 'POST'])
@per_required
def role_add():
    """
    角色新增
    :return:
    """
    logging.info('role_add')
    role_form = RoleForm()
    if role_form.validate_on_submit():
        name = role_form.data["name"]
        desc = role_form.data["desc"]
        org_id = role_form.data["org_id"]
        id = session.get("user_id", 0)
        sysuser = SysUser.query.filter_by(id=id).first()
        Rolelist.create(name=name, org_id=org_id, description=desc, create_by=sysuser.username,
                        create_time=datetime.now())
        # 发送操作消息
        message_view.add_option_message("新增角色 '" + name + "'", '新增角色')
        return redirect(url_for('sysrole.role'))  # sys_add_role
    id = session.get("user_id", 0)
    org_id = SysUser.query.filter_by(id=id).first().org_id
    org_code = SysOrg.query.filter_by(org_id=org_id).first()
    return render_template('sysadmin/sysrole/sys_add_role.html', **locals())


@csrf_protect.exempt
@blueprint.route('/role/edit/', methods=['GET', 'POST'])
@per_required
def role_edit_url():
    """
    角色编辑
    :return:
    """
    logging.info('role_edit_url')
    id = int(request.args.get("id"))
    role_form = RoleForm()  # 表单
    if request.method == "POST":
        if role_form.validate_edit(id):
            res = Rolelist.query.filter_by(id=id).first()  # 当前角色对象
            id = session.get("user_id", 0)
            sysuser = SysUser.query.filter_by(id=id).first()
            update_by = sysuser.username  # 更新人
            update_time = datetime.now()  # 更新时间
            Rolelist.update(res,
                            description=role_form.data["desc"],
                            org_id=role_form.data["org_id"],
                            name=role_form.data["name"],
                            update_by=update_by,
                            update_time=update_time)
            return redirect(url_for('sysrole.role'))
        else:
            return render_template('sysadmin/sysrole/sys_edit_role.html', **locals())
    role_form.init_data_edit_new(id)  # 初始化编缉的SELECT
    return render_template('sysadmin/sysrole/sys_edit_role.html', **locals())


@csrf_protect.exempt
@blueprint.route('/role/role_management/', methods=['GET', 'POST'])
@per_required
def role_management():
    """
    权限管理 角色授权
    :return: Permissionlist.query.all()
    """
    logging.info('role_management')
    try:
        id = int(request.args.get("id"))  # 获取配置角色ID
        user_id = session.get("user_id", 0)
        org_code = session.get('org_code', '0')

        sys_role = Rolelist.query.join(SysUserRole, SysUserRole.role_id == Rolelist.id).filter(SysUserRole.user_id == user_id).first()

        targetrole = Rolelist.query.filter_by(id=id).first()  # 目标ID对象
        if targetrole.status == "正常":
            keyvalue = True
        else:
            keyvalue = False
        role_form = RoleForm(manage=1)  # 表单
        role_form.init_data_edit(id)  # 初始化编缉的SELECT
        name = targetrole.name  # 管理目标角色的角色名
        description = targetrole.description  # 管理目标角色的角色描述
        list_info = Permissionlist.query.filter(not_(Permissionlist.type == 1),  # 当可选的全权限
                                                Permissionlist.status == 0,
                                                Permissionlist.del_flag == 0)

        if sys_role and org_code == '0001' and sys_role.name == '超级管理员':
            list_info = list_info.order_by(Permissionlist.sort.desc()).all()
        else:
            list_info = list_info.join(SysRolePermissionlist, SysRolePermissionlist.permissionlist_id == Permissionlist.id) \
                .join(SysUserRole, SysUserRole.role_id == SysRolePermissionlist.role_id).filter(SysUserRole.user_id == user_id) \
                .order_by(Permissionlist.sort.desc()).all()

        yeslist = []  # 右边的LIST
        for i in SysRolePermissionlist.query.filter_by(role_id=id).all():  # 当前已有的全部权限
            permission = Permissionlist.query.filter(Permissionlist.id == i.permissionlist_id,
                                                     not_(Permissionlist.type == 1),
                                                     Permissionlist.status == 0,
                                                     Permissionlist.del_flag == 0).first()
            if permission:
                yeslist.append(permission)
        list_info = list(set(list_info) - set(yeslist))  # 未选择的可选角色 左边的LIST
        list_info.sort(key=lambda k: k.sort)  # 排序
        yeslist.sort(key=lambda k: k.sort)
        if request.method == "POST":
            newinfo = list(request.form.getlist('duallistbox_rich'))
            desc = request.form.get('desc')  # 描述
            role_permission(id, newinfo)  # 给角色授权
            res = Rolelist.query.filter_by(id=id).first()  # 当前角色对象
            id = session.get("user_id", 0)
            sysuser = SysUser.query.filter_by(id=id).first()
            update_by = sysuser.username  # 更新人
            update_time = datetime.now()  # 更新时间
            Rolelist.update(res, description=desc, update_by=update_by, update_time=update_time)
            return redirect(url_for('sysrole.role'))
        return render_template('sysadmin/sysrole/sys_manage_role.html', **locals())
    except Exception as e:
        logging.error(e)
        return render_template('sysadmin/sysrole/sys_manage_role.html', **locals())


@csrf_protect.exempt
@blueprint.route('/role/changestatus/', methods=['GET', 'POST'])
@per_required
def role_changestatus():
    '''
      状态改变
    :return:
    '''
    logging.info('role_changestatus')
    id = int(request.args.get("id"))
    user_id = session.get('user_id')
    sys_user_role = SysUserRole.query.filter(SysUserRole.user_id == user_id, SysUserRole.role_id == id).first()
    if sys_user_role:
        return json.dumps({'code': ResponseCode.ERROR, 'desc': '用户自身不能被停用!'})
    res = Rolelist.query.filter_by(id=id).first()
    if res.status == "正常":
        Rolelist.update(res, status="停用")
    else:
        Rolelist.update(res, status="正常")

    # 发送操作消息
    message_view.add_option_message("更新角色 '" + res.name + "' 的状态", '更新角色')
    name_dict = {'code': "0", 'desc': '状态更新成功!'}
    return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/role/delete/', methods=['GET', 'POST'])
@per_required
def role_delete():
    '''
      删除角色
    :return:
    '''
    logging.info('role_delete')
    id = int(request.args.get("id"))
    obj = SysUserRole.query.filter_by(role_id=str(id)).first()
    if obj:
        name_dict = {'code': ResponseCode.ERROR, 'desc': '角色正在使用中不能删除!'}
        return json.dumps(name_dict)
    res = Rolelist.query.filter_by(id=id).first()
    # if res.name == 'flow_客服审核（系统默认）':
    #     name_dict = {'code': ResponseCode.ERROR, 'desc': '系统默认角色不能删除!'}
    #     return json.dumps(name_dict)
    # if res.name == 'flow_支付参数配置（系统默认）':
    #     name_dict = {'code': ResponseCode.ERROR, 'desc': '系统默认角色不能删除!'}
    #     return json.dumps(name_dict)
    Rolelist.delete(res)
    listinfo = SysRolePermissionlist.query.filter_by(role_id=id).all()
    for item in listinfo:
        SysRolePermissionlist.delete(item)
    # 发送操作消息
    message_view.add_option_message("删除角色 '" + res.name + "'", '删除角色')
    name_dict = {'code': ResponseCode.SUCCESS, 'desc': '角色删除成功!'}
    return json.dumps(name_dict)


def get_role_list():
    """
    获取所有角色列表数据
    :param :
    :return:
    """
    logging.info('get_role_list')
    try:
        data = []
        listdata = Rolelist.query.all()
        for role in listdata:
            data.append([
                role.id,
                role.id,
                role.name,
                role.description,
                role.status,
                role.id
            ])
        return data
    except Exception as e:
        logging.debug(e)
        raise e


def get_role_list_by_user(user_id, offset_data, page_size, search_data, sort, sortOrder):
    """
    获取角色列表数据 org_id 下面所有角色列表
    :param  org_id :
    :return:
    """
    logging.info('get_role_list_by')
    try:
        res_data = []
        temp = []
        org_code = session.get('org_code', 0)
        is_admin = session_user_is_admin()
        if is_admin:  # 超级管理员有所有权限
            listdata = db.session.query(Rolelist, SysOrg).filter(
                Rolelist.org_id == SysOrg.org_id,  # 角色机构ID与机构ID一一对应
                or_(Rolelist.name.like('%' + search_data + '%'),
                    Rolelist.description.like('%' + search_data + '%'),
                    Rolelist.role_type.like('%' + search_data + '%'),
                    Rolelist.status.like('%' + search_data + '%'),
                    SysOrg.org_name.like('%' + search_data + '%')))
        else:
            listobj = SysOrg.query.filter(SysOrg.org_code.like(org_code + '%')).all()
            for li_ in listobj:
                temp.append(li_.org_code)
            listdata = db.session.query(Rolelist, SysOrg).filter(
                # SysOrg.org_code.like(org_code + '%'),  # 机构编码在此操作用户机构编码的子编码一样
                SysOrg.org_code.in_(temp),
                Rolelist.org_id == SysOrg.org_id,  # 角色机构ID与机构ID一一对应
                or_(Rolelist.name.like('%' + search_data + '%'),
                    Rolelist.description.like('%' + search_data + '%'),
                    Rolelist.role_type.like('%' + search_data + '%'),
                    Rolelist.status.like('%' + search_data + '%'),
                    SysOrg.org_name.like('%' + search_data + '%')))
        all = listdata.order_by(sort_in_role_list(sort, sortOrder)).offset(offset_data).limit(page_size).all()
        len = listdata.count()
        # if search_data:
        #     len = listdata.with_entities(func.count(or_(
        #         Rolelist.name.like('%' + search_data + '%'),
        #         Rolelist.description.like('%' + search_data + '%'),
        #         Rolelist.role_type.like('%' + search_data + '%'),
        #         Rolelist.status.like('%' + search_data + '%'),
        #         SysOrg.org_name.like('%' + search_data + '%')
        #     ))).scalar()
        # else:
        #     len = listdata.with_entities(func.count(Rolelist.id))
        for item in all:
            dict = {}
            dict['id'] = item[0].id,
            dict['name'] = item[0].name,
            dict['status'] = item[0].status,
            dict['role_type'] = item[0].role_type,
            dict['description'] = item[0].description,
            dict['org_id'] = item[1].org_name
            res_data.append(dict)
        return res_data, len
    except Exception as e:
        logging.debug(e)
        raise e


def sort_in_role_list(sort, sortOrder):
    """
    排序
    :param sort:
    :param sortOrder:
    :return:
    """
    logging.info('sort_in_role_list')
    if sortOrder == 'asc':
        if sort == 'name':
            return Rolelist.name.asc()
        elif sort == 'description':
            return Rolelist.description.asc()
        elif sort == 'org_id':
            return SysOrg.org_id.asc()
        elif sort == 'role_type':
            return Rolelist.role_type.asc()
        elif sort == 'status':
            return Rolelist.status.asc()
        else:
            return None
            # Rolelist.id.asc()
    else:
        if sort == 'name':
            return Rolelist.name.desc()
        elif sort == 'description':
            return Rolelist.description.desc()
        elif sort == 'org_id':
            return SysOrg.org_id.desc()
        elif sort == 'role_type':
            return Rolelist.role_type.desc()
        elif sort == 'status':
            return Rolelist.status.desc()
        else:
            return None
            # return Rolelist.id.desc()


def role_add(name, description):
    """
    新增角色
    :param name:         名字
    :param description:  描述
    :return:
    """
    logging.info('role_add')
    try:
        data = Rolelist.create(name=name, description=description)
        # 发送操作消息
        message_view.add_option_message("新增角色 '" + name + "'", '新增角色')
        return {'code': ResponseCode.SUCCESS, 'data': data}
    except Exception as e:
        logging.debug(e)
        raise e


def role_update(id, name, description, status="正常"):
    """
    编辑角色  （包括更新状态  ）
    :param id:
    :param name:         名字
    :param description:  描述
    :param status:       状态
    :return:
    """
    logging.info('role_update')
    try:
        role = Rolelist.query.filter_by(id=id).first()
        data = Rolelist.update(role, description=description, status=status, name=name)
        # 发送操作消息
        message_view.add_option_message("更新角色 '" + name + "' 的信息", '更新角色')
        return {'code': ResponseCode.SUCCESS, 'data': data}
    except Exception as e:
        logging.debug(e)
        raise e


def role_permission(role_id, listpower):
    """
    角色授权
    :param role_id:     角色ID
    :param listpower:   角色授权的权限列表  list 新的权限ID列表对象
    :return:
    """
    logging.info('role_permission')
    try:
        info = []  # 公共集合
        oldpower = SysRolePermissionlist.query.filter_by(role_id=role_id).all()
        for item in oldpower:  # 删差集权限
            if str(item.permissionlist_id) in listpower:
                info.append(str(item.permissionlist_id))
            else:
                permission_status = Permissionlist.query.filter_by(id=item.permissionlist_id).first()
                if permission_status:
                    if permission_status.status == 0:  # status
                        SysRolePermissionlist.delete(item)  # 2017.10.31 ping
        for i in list(set(listpower) ^ set(info)):  # 增加新附加的权限
            SysRolePermissionlist.create(role_id=role_id, permissionlist_id=i)
        the_role = Rolelist.query.filter_by(id=role_id).first()
        # 发送操作消息
        message_view.add_option_message("更新角色 '" + the_role.name + "' 的信息", '更新角色')
        return {'code': ResponseCode.SUCCESS}
    except Exception as e:
        logging.debug(e)
        raise e


def role_only(name):
    """
    添加新角色时不能有重用名
    :param name:
    :return:
    """
    logging.info('role_only')
    try:
        res = Rolelist.query.filter_by(name=name).first()
        if res is None:
            return {'code': ResponseCode.SUCCESS}
        else:
            return {'code': ResponseCode.ERROR}
    except Exception as e:
        logging.debug(e)
        raise e
