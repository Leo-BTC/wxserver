#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/26 18:29
# @Author  : wangzhouyang
# @Site    : www.rich-f.com
# @File    : user_view.py
# @Software: 富融钱通系统
# @Function: 用户管理模块
import base64, time
import logging, os
import platform
from flask import json, session, request, redirect, url_for, current_app
from flask_login import login_required
from sqlalchemy import or_
from test.extensions import db, mail, csrf_protect
from test.responsecode import ResponseCode
from test.sysadmin import message_view
from test.sysadmin.models import SysUser, SysOrg, Rolelist, SysUserRole, SysUserHistory, SysDict
from flask import Blueprint, render_template
from test.sysadmin.forms import UserForm, PasswordForm
from test.sysadmin.permission_required import per_required
from test.utils import get_current_time, generate_verification_code
from flask_mail import Message

blueprint = Blueprint('sysuser', __name__, url_prefix='/sysuser', static_folder='../static')


@csrf_protect.exempt
@blueprint.route('/update/user/<id>', methods=['GET', 'POST'])
@blueprint.route('/add/user/<id>', methods=['GET', 'POST'])
@per_required
def add_user(id):
    """
    系统用户新增界面
    :return:
    """
    logging.info('add_user')
    user_form = UserForm(id)
    if user_form.validate_on_submit():
        data = request.form
        if deal_user_info(data, user_form):
            return redirect(url_for('sysuser.user'))
    else:
        flag = '-1'
        if user_form.is_submitted():
            pass
        else:
            if user_form.title_name == '编辑用户信息':
                user_form.init_data(id)
                # 判断编辑的用户是否为超级管理员，如果是，则其角色不容更改
                role = db.session.query(Rolelist.name).filter(SysUserRole.user_id == id,
                                                              SysUserRole.role_id == Rolelist.id).all()
                if role[0][0] == '超级管理员':
                    flag = '0'
        return render_template('sysadmin/sysuser/sys_add_user.html', user_form=user_form, flag=flag)


def deal_user_info(data, user_form):
    """
    处理用户表单数据
    :param data:
    :param user_form:
    :return:
    """
    logging.info('deal_user_info')
    try:
        if user_form.id == '0':
            return add_user_info(data)
        else:
            obj = SysUser.query.filter_by(id=user_form.id).first()
            return update_user(obj, data)
    except Exception as e:
        logging.debug(e)
        raise e


@blueprint.route('/to/get/org/role')
@login_required
def to_get_role_by_org_id():
    """
    通过机构id获取角色
    :return:
    """
    logging.info('to_get_role_by_org_id')
    org_id = request.args.get('org_id')
    role_list = db.session.query(Rolelist.name, Rolelist.id).filter(Rolelist.org_id == org_id,
                                                                    Rolelist.name != '超级管理员').all()
    res = []
    for item in role_list:
        data = [item[1], item[0]]
        res.append(data)
    return json.dumps(res)


@blueprint.route('/get/all/org')
@login_required
def get_all_org_name():
    """
    获取所有机构名字
    :return:
    """
    logging.info('get_all_org_name')
    org_list = SysOrg.query.all()
    data = []
    for item in org_list:
        temp = [item.org_id, item.org_name]
        data.append(temp)
    res_data = {'data': data}
    return json.dumps(res_data)


@blueprint.route('/')
@per_required
def user():
    """
    系统用户界面
    :return:
    """
    logging.info('user')
    return render_template('sysadmin/sysuser/sysuser.html')


@csrf_protect.exempt
@blueprint.route('/person/info', methods=['GET', 'POST'])
@per_required
def person_info():
    """
    个人信息界面
    :return:
    """
    logging.info('person_info')
    data = request.data
    user_id = session['user_id']
    user_form = UserForm(user_id)  ##
    if user_form.validate_on_submit():
        data = request.form
        obj = SysUser.query.filter_by(id=user_id).first()
        update_user(obj, data)
        return redirect(url_for('sysuser.person_info'))
    else:
        if user_form.is_submitted():
            obj = SysOrg().query.filter_by(org_id=user_form.org.data).first()
            org_name = obj.org_name
            role_name = db.session.query(Rolelist.name).filter(SysUserRole.user_id == user_id,
                                                               Rolelist.id == SysUserRole.role_id).first()[0]
        else:
            user_form.init_data(user_id)
            obj = SysOrg().query.filter_by(org_id=user_form.org.data).first()
            org_name = obj.org_name
            role_id = user_form.role.data
            role = Rolelist().query.filter_by(id=int(role_id)).first()
            role_name = role.name
        return render_template('sysadmin/sysuser/self_info.html', user_form=user_form, org_name=org_name,
                               role_name=role_name)


def save_image(img):
    """
        保存图片到本地目录
        :return:
        """
    logging.info('save_image')
    try:
        if img is not None:
            img = img.split(',')[1]
            imgdata = base64.b64decode(img)
            current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            CURRENT_SYSTEM = platform.system()
            if CURRENT_SYSTEM == 'Windows':
                image_path = current_path + '\\static\\images\\avatar\\'
            else:
                image_path = current_path + '/static/images/avatar/'
            file = open(image_path + str(int(time.time())) + '.png', 'wb +')
            logging.info(file)
            file.write(imgdata)
            file.close()
            image_url = str(int(time.time())) + '.png'
        return image_url
    except Exception as e:
        logging.debug(e)
        raise e


@csrf_protect.exempt
@blueprint.route('/change/password', methods=['POST', 'GET'])
@per_required
def change_password():
    """
    修改密码界面
    :return:
    """
    logging.info('change_password')
    password_form = PasswordForm()
    if password_form.validate_on_submit():
        to_reset_password(password_form)
        return redirect(url_for('public.logout'))
    else:
        return render_template('sysadmin/sysuser/reset_password.html', password_form=password_form)


@blueprint.route('/user/list')
@login_required
def get_user_list():
    """
    获取当前登录用户下的所属机构的下属所有机构的人员名单
    :param userId:登录的用户对象
    :return:
    """
    logging.info('get_user_list')
    try:
        user_id = session.get('user_id', 0)
        page_number = request.args.get('pageNumber')
        page_size = request.args.get('pageSize')
        sort = request.args.get('sort')
        sortOrder = request.args.get('sortOrder')
        offset_data = (int(page_number))
        search_data = request.args.get('searchData')
        logging.info('search_data:%s' + str(search_data))
        if search_data:
            offset_data = 0
        else:
            search_data = ''

        org_id = get_org_id_by_user_id(user_id).org_id  # 根据用户id获取其所属机构的机构id
        org_list = get_all_child_org_by_org_id(org_id)  # 根据公司id获取其下属所有机构（包括其本身）
        org_id_list = []

        for item in org_list:
            org_id_list.append(item.org_id)
        user_list = get_user_by_org_id(org_id_list, offset_data, page_size, search_data, sort,
                                       sortOrder)  # 根据机构id列表查询用户以及机构名称

        all_data_count = get_user_all_count_by_org_id(org_id_list, search_data)
        res_data = []

        for item in user_list:
            role_list = get_role_by_user_id(item[0].id)  # 根据用户id获取角色信息
            role_data = []
            for role in role_list:
                role_data.append(role.name)
            org_name = '无'
            org = SysOrg.query.filter_by(org_id=item[0].org_id).first()
            if org:
                org_name = org.org_name
            dict = {}
            dict['id'] = item[0].id
            dict['username'] = item[0].username,
            dict['mobile'] = item[0].mobile,
            dict['email'] = item[0].email,
            dict['org_name'] = org_name
            dict['role'] = role_data,
            dict['update_time'] = str(item[0].update_time),
            # if item[0].id == session.get('user_id'):
            #     dict['login_time'] = str(session.get('last_login'))
            # else:
            dict['login_time'] = str(item[0].last_login)
            if dict['login_time'] == 'None':
                dict['login_time'] = '-----------'
            dict['status'] = item[0].is_active,
            dict['id'] = item[0].id
            res_data.append(dict)
        req_data = {'total': all_data_count, 'rows': res_data}
        return json.dumps(req_data)
    except Exception as e:
        logging.debug(e)
        raise e


@blueprint.route('/reset/password/<id>', methods=['GET'])
@per_required
def reset_password(id):
    """
    用户管理--重置密码
    通过id查询到用户，获取用户姓名，用户邮箱，通过随机生成六位数密码，发送给用户邮箱
    :return:
    """
    logging.info('reset_password')
    try:
        new_password = generate_verification_code()
        sys_user = SysUser.query.filter_by(id=id).first()

        if sys_user:
            address = sys_user.email
            msg = Message('富融通密码重置', sender='service@rich-f.com', recipients=[address])
            msg.body = '邮件内容'
            msg.html = "<h1>密码重置成功！<h1> <div>" + sys_user.name + "您好：</div><div>我们收到了来自您的富融通用户密码重置的申请。请使用下面的密码进行登录，并尽快设置新的密码。以下是您的密码：</div><h2>" + new_password + "<h2><div>富融通</div>"
            with current_app.app_context():
                mail.send(msg)
            new_password = SysUser.set_password(sys_user, new_password)
            SysUser.update(sys_user, password=new_password)
            # 发送操作消息
            message_view.add_option_message("重置用户 '" + sys_user.username + "' 的密码")
            return json.dumps({'code': ResponseCode.SUCCESS})
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'msg': '重置密码失败'}
        return json.dumps(name_dict)


@blueprint.route('/delete/user/<id>', methods=['GET'])
@per_required
def delete_user(id):
    """
    用户管理--删除用户
    :param id:
    :return:
    """
    logging.info('delete_user')
    try:
        sys_user = SysUser.query.filter_by(id=id).first()
        sys_role = SysUserRole.query.filter_by(user_id=id).first()
        sys_user_history = SysUserHistory.query.filter_by(user_id=id).first()
        if sys_user:
            # 用户表用户信息删除
            SysUser.delete(
                sys_user
            )
            # 用户角色信息删除
            SysUserRole.delete(
                sys_role
            )
            # 用户历史表
            SysUserHistory.update(
                sys_user_history,
                status='0',
                update_time = get_current_time(),
                end_time = get_current_time(),
                update_by = session.get('user_name')
            )
            # 发送操作消息
            message_view.add_option_message("删除用户 '" + sys_user.username + "'")
            res = {'code': ResponseCode.SUCCESS, 'msg': '删除成功'}
            return json.dumps(res)
    except Exception as e:
        logging.debug(e)
        raise e


def get_user_info(user_id):
    """
    根据用户ID获取用户信息
    :param user_id:
    :return:
    """
    logging.info('get_user_info')
    data = get_info_by_user_id(user_id)  # 通过用户id获取用户信息
    role_list = get_role_by_user_id(user_id)  # 根据用户id获取角色信息
    role = []
    for item in role_list:
        role.append(item.id)
    info = {
        'username': data[0].username,
        'name': data[0].name,
        'mobile': data[0].mobile,
        'email': data[0].email,
        'sex': data[0].sex,
        'is_active': data[0].is_active,
        'org_name': data[1],
        'role': role,
    }
    return info


@blueprint.route('/close/user/<id>')
@per_required
def close_user(id):
    """
    根据用户id停用用户
    :param id:
    :return:
    """
    logging.info('close_user')
    role = db.session.query(Rolelist.name).filter(SysUserRole.user_id == id, Rolelist.id == SysUserRole.role_id).first()
    if role[0] == '超级管理员':
        res = {'code': ResponseCode.ERROR}
    else:
        temp = close_user_by_user_id(id)
        res = {'code': ResponseCode.SUCCESS}
    return json.dumps(res)


@blueprint.route('/open/user/<id>')
@per_required
def open_user(id):
    """
    根据用户id启用用户
    :param id:
    :return:
    """
    logging.info('open_user')
    temp = open_user_by_user_id(id)
    res = {'code': ResponseCode.SUCCESS}
    return json.dumps(res)


@blueprint.route('/get/edit/user/one/org/data', methods=['GET'])
@login_required
def get_edit_user_one_org_data():
    """
    获取用户编辑的机构org_id
    :return:
    """
    logging.info('get_edit_user_one_org_data')
    try:
        params = request.values.to_dict()
        org_id = params['org_id']
        if org_id == '':
            return json.dumps({'code': ResponseCode.ERROR})
        one_org_data = report_edit_user_get_org_data(org_id)
        return json.dumps(one_org_data)
    except Exception as e:
        logging.debug(e)
        raise e


@blueprint.route('/get/edit/user/one/org/code/data', methods=['GET'])
@login_required
def get_edit_user_one_org_code_data():
    """
    获取用户编辑的org_code
    :return:
    """
    logging.info('get_edit_user_one_org_code_data')
    try:
        params = request.values.to_dict()
        org_code = params['org_code']
        if org_code == '':
            return json.dumps({'code': ResponseCode.ERROR})
        one_org_data = report_edit_user_get_org_code_data(org_code)
        return json.dumps(one_org_data)
    except Exception as e:
        logging.debug(e)
        raise e


def get_org_id_by_user_id(user_id):
    """
    根据用户ID获得其所属机构（商户）
    :param user_id:用户id
    :return:其所属机构的对象
    """
    logging.info('get_org_id_by_user_id')
    try:
        return db.session.query(SysOrg).filter(SysOrg.org_id == SysUser.org_id, SysUser.id == user_id).first()
    except Exception as e:
        logging.debug(e)
        raise e


def get_all_child_org_by_org_id(org_id):
    """
    根据机构ID查询所有下属机构（包括本身）
    :param org_id:
    :return:
    """
    logging.info('get_all_child_org_by_org_id')
    try:
        sys_org = SysOrg.query.filter_by(org_id=org_id).first()
        if sys_org:
            return SysOrg.query.filter(SysOrg.org_code.like(sys_org.org_code + '%')).all()
    except Exception as e:
        logging.debug(e)
        raise e


def get_user_by_org_id(org_id_list, offset_data, page_size, search_data, sort, sortOrder):
    """
    根据机构id列表查询用户信息以及机构名字
    :param org_id_list:机构id列表
    :return:用户对象，机构名称
    """
    logging.info('get_user_by_org_id')
    try:
        return db.session.query(SysUser, SysOrg.org_name).filter(SysUser.org_id.in_(org_id_list),
                                                                 SysUser.org_id == SysOrg.org_id,
                                                                 Rolelist.id == SysUserRole.role_id,
                                                                 SysUserRole.user_id == SysUser.id,
                                                                 or_(SysUser.org_id.like('%' + search_data + '%'),
                                                                     SysUser.username.like('%' + search_data + '%'),
                                                                     SysUser.mobile.like('%' + search_data + '%'),
                                                                     SysUser.email.like('%' + search_data + '%'),
                                                                     SysOrg.org_name.like('%' + search_data + '%'),
                                                                     SysUser.is_active.like(
                                                                         '%' + is_statu(search_data) + '%'),
                                                                     Rolelist.name.like(
                                                                         '%' + search_data + '%'))).order_by(
            sort_in_sysuser(sort, sortOrder)).offset(
            offset_data).limit(page_size).all()
    except Exception as e:
        logging.debug(e)
        raise e


def is_statu(search_data):
    """
    判断是否有参数，且为正常还是停用
    :param search_data:
    :return:
    """
    logging.info('is_statu')
    if search_data:
        if search_data == '正常':
            return '1'
        elif search_data == '停用':
            return '0'
        else:
            return search_data
    else:
        return ''


def sort_in_sysuser(data, sortOrder):
    """
    判断排序条件
    :param data:
    :param sortOrder:
    :return:
    """
    logging.info('sort_in_sysuser')
    if sortOrder == 'asc':
        if data == 'username':
            return SysUser.username.asc()
        elif data == 'mobile':
            return SysUser.mobile.asc()
        elif data == 'email':
            return SysUser.email.asc()
        elif data == 'id':
            return SysUser.id.asc()
        elif data == 'org_name':
            return SysOrg.org_name.asc()
        elif data == 'role':
            return Rolelist.name.asc()
        elif data == 'status':
            return SysUser.is_active.asc()
        elif data == 'login_time':
            return SysUser.last_login.asc()
        elif data == 'update_time':
            return SysUser.update_time.asc()
        else:
            return ''
    else:
        if data == 'username':
            return SysUser.username.desc()
        elif data == 'mobile':
            return SysUser.mobile.desc()
        elif data == 'email':
            return SysUser.email.desc()
        elif data == 'id':
            return SysUser.id.desc()
        elif data == 'org_name':
            return SysOrg.org_name.desc()
        elif data == 'role':
            return Rolelist.name.desc()
        elif data == 'status':
            return SysUser.is_active.desc()
        elif data == 'login_time':
            return SysUser.last_login.desc()
        elif data == 'update_time':
            return SysUser.update_time.desc()
        else:
            return SysUser.update_time.desc()


def get_user_all_count_by_org_id(org_id_list, search_data):
    """
    获取机构下用户数量
    :param org_id_list:
    :return:
    """
    logging.info('get_user_all_count_by_org_id')
    try:
        return db.session.query(SysUser, SysOrg.org_name).filter(SysUser.org_id.in_(org_id_list),
                                                                 SysUser.org_id == SysOrg.org_id,
                                                                 Rolelist.id == SysUserRole.role_id,
                                                                 SysUserRole.user_id == SysUser.id,
                                                                 or_(SysUser.org_id.like('%' + search_data + '%'),
                                                                     SysUser.username.like('%' + search_data + '%'),
                                                                     SysUser.mobile.like('%' + search_data + '%'),
                                                                     SysUser.email.like('%' + search_data + '%'),
                                                                     SysOrg.org_name.like('%' + search_data + '%'),
                                                                     SysUser.is_active.like(
                                                                         '%' + is_statu(search_data) + '%'),
                                                                     Rolelist.name.like(
                                                                         '%' + search_data + '%'))).count()
    except Exception as e:
        logging.debug(e)
        raise e


def get_role_by_user_id(user_id):
    """
    通过用户id查询角色名称
    :param user_id: 用户id
    :return:
    """
    logging.info('get_role_by_user_id')
    try:
        return db.session.query(Rolelist.name).filter(SysUserRole.user_id == user_id,
                                                      SysUserRole.role_id == Rolelist.id).all()
    except Exception as e:
        logging.debug(e)
        raise e


def get_info_by_user_id(user_id):
    """
    通过用户id获取用户信息
    :param user_id:
    :return:
    """
    logging.info('get_info_by_user_id')
    try:
        return db.session.query(SysUser, SysOrg.org_name).filter(SysUser.id == user_id,
                                                                 SysUser.org_id == SysOrg.org_id).first()
    except Exception as e:
        logging.debug(e)
        raise e


def close_user_by_user_id(user_id):
    """
    根据用户id修改数据库字段is_active为0
    :param user_id:用户id
    :return:
    """
    logging.info('close_user_by_user_id')
    try:
        obj = SysUser.query.filter_by(id=user_id).first()
        # 发送操作消息
        message_view.add_option_message("更改用户 '" + obj.username + "' 的状态为停用")
        return SysUser.update(obj, is_active=0, update_time=get_current_time(), update_by=session.get('user_name'))
    except Exception as e:
        logging.debug(e)
        raise e


def open_user_by_user_id(user_id):
    """
    根据用户id修改数据库字段is_active为1
    :param user_id: 用户id
    :return:
    """
    logging.info('open_user_by_user_id')
    try:
        obj = SysUser.query.filter_by(id=user_id).first()
        # 发送操作消息
        message_view.add_option_message("更改用户 '" + obj.username + "' 的状态为正常")
        return SysUser.update(obj, is_active=1, update_time=get_current_time(), update_by=session.get('user_name'))
    except Exception as e:
        logging.debug(e)
        raise e


def get_all_role_by_org_id(user_id):
    """
    根据用户id查询到其所属机构拿到机构id
    根据机构id查询其所有角色名称
    :param user_id: 用户id
    :return:
    """
    logging.info('get_all_role_by_org_id')
    try:
        ret = db.session.query(Rolelist).filter(SysUser.id == user_id, Rolelist.org_id == SysUser.org_id).all()
        return ret
    except Exception as e:
        logging.debug(e)
        raise e


def add_user_info(data):
    """
    用户信息插入数据库
    :param data: 表单数据
    :return:
    """
    logging.info('add_user_info')
    try:
        user_id = session.get('user_id', 0)
        sys_user = SysUser.query.filter_by(id=user_id).first()
        image_list = data.getlist('image')
        for temp in image_list:
            if 'data' in temp:
                image_url = save_image(temp)
            else:
                image_url = 'default.png'
        if sys_user:
            SysUser.create(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                mobile=data['mobile'],
                name=data['name'],
                chat_code=data['chat_code'],
                avatar=image_url,
                desc=data['desc'],
                sex=data['sex'],
                is_active=data['is_active'],
                org_id=data['org'],
                create_time=get_current_time(),
                update_time=get_current_time(),
                create_by=sys_user.username
            )
            # 发送操作消息
            message_view.add_option_message("新增用户 '" + data['username'] + "'")
            new = db.session.query(SysUser.id).filter(SysUser.username == data['username']).first()
            SysUserRole.create(
                user_id=new[0],
                username=data['username'],
                role_id=data['role'],
                org_id=data['org'],
                create_time=get_current_time(),
                create_by=sys_user.username
            )
            SysUserHistory.create(
                user_id=new[0],
                mobile=data['mobile'],
                email=data['email'],
                chat_code=data['chat_code'],
                org_id=data['org'],
                status=data['is_active'],
                create_time=get_current_time(),
                create_by=sys_user.username,
                start_time=get_current_time()
            )
            return True
    except Exception as e:
        logging.debug(e)
        raise e


def update_user(obj, data):
    """
    更新用户信息
    :param obj:
    :param data:
    :return:
    """
    logging.info('update_user')
    try:
        user_id = session.get('user_id', 0)
        sys_user = SysUser.query.filter_by(id=user_id).first()
        sys_user_history = SysUserHistory.query.filter_by(user_id=obj.id).first()
        if obj.org_id != data['org']:
            SysUserHistory.update(
                sys_user_history,
                update_by=session.get('user_name'),
                update_time=get_current_time(),
                end_time=get_current_time()
            )
            SysUserHistory.create(
                user_id=obj.id,
                org_id=data['org'],
                status=data['is_active'],
                create_time=get_current_time(),
                create_by=session.get('user_name'),
                start_time=get_current_time()
            )
        image_list = data.getlist('image')
        for temp in image_list:
            if 'data' in temp:
                image_url = save_image(temp)
            else:
                image_url = obj.avatar
        if sys_user:
            SysUser.update(
                obj,
                username=data['username'],
                email=data['email'],
                mobile=data['mobile'],
                name=data['name'],
                chat_code=data['chat_code'],
                avatar=image_url,
                desc=data['desc'],
                sex=data['sex'],
                org_id=data['org'],
                is_active=data['is_active'],
                update_time=get_current_time(),
                update_by=sys_user.username
            )
            # 发送操作消息
            message_view.add_option_message("更新用户 '" + obj.username + "' 的信息")
            role_obj = SysUserRole.query.filter_by(user_id=obj.id).first()
            if data['role'] == '':
                pass
            else:
                if role_obj:
                    SysUserRole.update(
                        role_obj,
                        role_id=data['role'],
                        org_id=data['org'],
                        update_time=get_current_time(),
                        update_by=sys_user.username
                    )
                else:
                    SysUserRole.create(
                        user_id=obj.id,
                        username=data['username'],
                        role_id=data['role'],
                        org_id=data['org'],
                        create_time=get_current_time(),
                        create_by=sys_user.username
                    )
            if obj.id == session['user_id']:
                session['avatar'] = SysUser.query.filter_by(id=session['user_id']).first().avatar
        return True
    except Exception as e:
        logging.debug(e)
        raise e


def innit_form_data(obj, user_form):
    """
    初始化表单数据
    :param obj:
    :param dict:
    :return:
    """
    logging.info('innit_form_data')
    try:
        user_form.username.data = obj.username
        user_form.sex.data = obj.sex
        user_form.is_active.data = str(obj.is_active)
        user_form.org.data = obj.org_id
        user_form.name.data = obj.name
        user_form.email.data = obj.email
        user_form.mobile.data = obj.mobile
        return user_form
    except Exception as e:
        logging.debug(e)
        raise e


def to_reset_password(res_form):
    """
    重置密码
    :param data:
    :return:
    """
    logging.info('to_reset_password')
    try:
        new_password = res_form.data.get('newpassword')
        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        new_password = SysUser.set_password(user, new_password)
        SysUser.update(user, password=new_password, update_time=get_current_time(), update_by=session.get('user_name'))
        # 发送操作消息
        message_view.add_option_message("重置用户 '" + user.username + "' 的密码")
    except Exception as e:
        logging.debug(e)
        raise e


@csrf_protect.exempt
@blueprint.route('/test', methods=['GET','POST'])
def test():
    postdata = request.values.get('postdata')
    a =1
    return postdata