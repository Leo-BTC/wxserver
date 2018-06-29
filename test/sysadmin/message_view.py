#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/6 下午1:49
# @Author  : Lee才晓
# @Site    : www.rich-f.com
# @File    : message_view.py
# @Software: 富融钱通
# @Function: 消息管理模块逻辑操作
import logging

import time
from datetime import datetime

from flask import render_template, Blueprint, request, json, redirect, url_for, session
from flask_login import login_required
from flask_socketio import emit
from sqlalchemy import or_

from test.extensions import csrf_protect, db, socket_io
from test.responsecode import ResponseCode
from test.sysadmin.forms import MessageForm
from test.sysadmin.models import SysMessage, SysUser, SysDict, SysUserRole, Rolelist
from test.sysadmin.permission_required import per_required
from test.utils import flash_errors

blueprint = Blueprint('sysmsg', __name__, url_prefix='/sysmsg', static_folder='../static')


###########路由地址区域####################
@blueprint.route('/msg_send', methods=['GET'])
@per_required
def msg():
    """
    消息管理主界面
    :return:
    """
    return render_template('sysadmin/sysmsg/sys_msg_send.html', **locals())


@blueprint.route('/msg_received', methods=['GET'])
@per_required
def msg_receiver():
    """
    消息已收界面
    :return:
    """
    return render_template('sysadmin/sysmsg/sys_msg_received.html', **locals())


@csrf_protect.exempt
@blueprint.route('/msg/get_send_list', methods=['GET', 'POST'])
@login_required
def msg_get_list():
    """
        获取已发消息列表
        :return:
        """
    logging.info('msg_get_list')
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

        msg_data = get_all_send_message_with_limit(offset_data, page_size, search_data, sort, sortOrder)
        return json.dumps(msg_data)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '获取失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/msg/get_received_list', methods=['GET', 'POST'])
@login_required
def get_received_list():
    """
    获取已收消息列表
    :return:
    """
    logging.info('get_received_list')
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
        msg_data = get_all_received_message_with_limit(offset_data, page_size, search_data, sort, sortOrder)
        return json.dumps(msg_data)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '获取失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/get_detail/<id>/<page>', methods=['GET', 'POST'])
@per_required
def msg_get_detail(id, page):
    """
       消息详情界面
       :param id:
       :return:
       """
    logging.info('msg_get_detail')
    try:
        old_data = {}
        msg = get_the_msg_by_id(id)
        old_data['id'] = id
        old_data['msg_title'] = msg.msg_title
        # old_data['msg_content'] = msg.msg_content.split(',')
        old_data['msg_content'] = msg.msg_content
        old_data['msg_content_size'] = len(msg.msg_content.split(','))
        old_data['msg_date'] = "接收时间：" + msg.msg_date.strftime("%Y-%m-%d %H:%M:%S")
        old_data['msg_sender'] = "发送人：" + msg.msg_sender

        list = eval(msg.msg_receiver)
        msg_receiver = ""
        for i in range(len(list)):
            user = SysUser.query.filter_by(id=list[i][0]).first()
            if user is not None:
                msg_receiver += user.username + '; '

        old_data['msg_receiver'] = "接收人：" + msg_receiver
        old_data['page'] = page

        user_id = str(session.get('user_id', 0))
        set_msg_read_state(id, user_id)

        return render_template('sysadmin/sysmsg/sys_msg_detail.html', data=old_data)
    except Exception as e:
        logging.debug(e)
        return None


@csrf_protect.exempt
@blueprint.route('/get_content/<id>', methods=['GET', 'POST'])
@login_required
def get_content(id):
    msg = get_the_msg_by_id(id)
    name_dict = {'code': ResponseCode.SUCCESS, 'desc': '删除成功!', 'data': msg.msg_content}
    return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/msg_delete/<arr>', methods=['GET', 'POST'])
@login_required
def msg_delete(arr):
    """
        删除发件人消息
        :param id:
        :return:
        """
    logging.info("msg_delete")
    try:
        arr = arr.split(',')
        for i in range(len(arr)):
            msg_id = arr[i]
            delete_the_send_msg(msg_id)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '删除成功!', 'data': []}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '删除失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/msg_receiver_delete/<arr>', methods=['GET', 'POST'])
@login_required
def msg_receiver_delete(arr):
    """
            删除收件人消息
            :param id:
            :return:
            """
    logging.info("msg_receiver_delete")
    try:
        arr = arr.split(',')
        for i in range(len(arr)):
            msg_id = arr[i]
            delete_the_msg(msg_id)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '删除成功!', 'data': []}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '删除失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/msg_add', methods=['GET', 'POST'])
@per_required
def msg_add():
    """
    发送消息
    :return:
    """
    logging.info("msg_add")

    try:
        msg_form = MessageForm(request.form)

        if msg_form.is_submitted():
            data = request.form
            if msg_form.validate(data):

                add_message(data)
                return redirect(url_for('sysmsg.msg'))
            else:
                flash_errors(msg_form)
        return render_template('sysadmin/sysmsg/sys_msg_add.html', **locals())
    except Exception as e:
        logging.debug(e)


@csrf_protect.exempt
@blueprint.route('/get_msg_not_read_url', methods=['GET', 'POST'])
@login_required
def get_msg_not_read_url():
    """
    获取未读消息
    :param username:
    :return:
    """
    logging.info("get_msg_not_read_url")
    try:
        user_id = str(session.get('user_id', 0))
        msg_list_sql = SysMessage.query.filter(
            SysMessage.msg_receiver.like("%['" + user_id + "', '0', '0']%")).order_by(
            db.desc(SysMessage.msg_date))
        msg_list = msg_list_sql.limit(5).all()
        number = str(len(msg_list_sql.all()))
        data = []
        for msg in msg_list:
            item = {}
            item['msg_title'] = msg.msg_title
            item['id'] = msg.id
            data.append(item)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '更新状态成功!', 'data': data, 'number': number}
        return json.dumps(name_dict)
    except Exception as e:
        logging.debug(e)
        name_dict = {'code': ResponseCode.ERROR, 'desc': '更新状态失败!', 'data': []}
        return json.dumps(name_dict)


###########路由地址区域结束####################


#############逻辑操作区域###################

def add_option_message(content):
    """
    添加操作消息
    :param data:
    :return:
    """

    logging.info("add_option_message")
    try:
        dict = SysDict.query.filter_by(dict_name='通知消息').first()
        data = {}
        data['title'] = '新的通知消息'
        data['type'] = dict.dict_id
        data['content'] = content

        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        msg_id = 'M' + str(int(time.time()))

        msg_receiver = []
        msg_receiver.append([str(user_id), '0', '0'])
        db.session.add(SysMessage(msg_id=msg_id, msg_title=data['title'], msg_content=data['content'],
                          msg_type=data['type'],
                          msg_sender=user.username,
                          msg_receiver=str(msg_receiver),
                          create_by=user.username,
                          update_by=user.username))
        db.session.commit()
        # SysMessage.create(msg_id=msg_id, msg_title=data['title'], msg_content=data['content'],
        #                   msg_type=data['type'],
        #                   msg_sender=user.username,
        #                   msg_receiver=str(msg_receiver),
        #                   create_by=user.username,
        #                   update_by=user.username)

        result = {}
        result['msg_id'] = msg_id
        result['msg_title'] = data['title']
        result['msg_type'] = data['type']
        result['msg_sender'] = str(user_id)
        result['msg_receiver'] = str(msg_receiver)

        emit("sys_msg", {'data': result}, broadcast=True, namespace='/msg')
    except Exception as e:
        logging.debug(e)
        raise e


def add_customer_message(content):
    """
    添加客服消息
    :return: 
    """
    try:

        dict = SysDict.query.filter_by(dict_name='通知消息').first()
        data = {}
        data['title'] = '新的通知消息'
        data['type'] = dict.dict_id
        data['content'] = content

        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        msg_id = 'M' + str(int(time.time()))
        msg_receiver = []
        msg_receiver.append([str(user_id), '0', '0'])
        users = db.session.query(SysUserRole.user_id).filter(
            Rolelist.org_id == 'G20171028001', Rolelist.name.like('%' + u'客服' + '%'), Rolelist.id == SysUserRole.role_id
        ).all()
        for i in users:
            msg_receiver.append([str(i[0]), '0', '0'])

        SysMessage.create(msg_id=msg_id, msg_title=data['title'], msg_content=data['content'],
                          msg_type=data['type'],
                          msg_sender=user.username,
                          msg_receiver=str(msg_receiver),
                          create_by=user.username,
                          update_by=user.username)

        result = {}
        result['msg_id'] = msg_id
        result['msg_title'] = data['title']
        result['msg_type'] = data['type']
        result['msg_sender'] = str(user_id)
        result['msg_receiver'] = str(msg_receiver)

        emit("sys_msg", {'data': result}, broadcast=True, namespace='/msg')

    except Exception as e:
        logging.debug(e)


def add_message(data):
    """
    新增消息
    :param data:
    :return:
    """
    logging.info("add_message")
    try:
        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()
        msg_id = 'M' + str(int(time.time()))
        # s = data['content']
        # if s:
        #     re_br = re.compile('<br\s*?/?>')  # 处理换行
        #     re_h = re.compile('</?\w+[^>]*>')  # HTML标签
        #     s = re_br.sub('\n', s)  # 将br转换为换行
        #     s = re_h.sub('', s)  # 去掉HTML 标签
        msg_receiver = []

        id_receiver = data.getlist("receiver")
        for i in range(len(id_receiver)):
            msg_receiver.append([id_receiver[i], '0', '0'])

        SysMessage.create(msg_id=msg_id, msg_title=data['title'], msg_content=data['content'],
                          msg_type=data['type'],
                          msg_sender=user.username,
                          msg_receiver=str(msg_receiver),
                          create_by=user.username,
                          update_by=user.username)

        result = {}
        result['msg_id'] = msg_id
        result['msg_title'] = data['title']
        result['msg_type'] = data['type']
        result['msg_sender'] = str(user_id)
        result['msg_receiver'] = str(msg_receiver)

        emit("sys_msg", {'data': result}, broadcast=True, namespace='/msg')
    except Exception as e:
        logging.debug(e)


def get_msg_not_read(user_id):
    """
    获取未读消息
    :param username:
    :return:
    """
    try:
        msg_list_sql = SysMessage.query.filter(
            SysMessage.msg_receiver.like("%['" + user_id + "', '0', '0']%")).order_by(
            db.desc(SysMessage.msg_date))
        msg_list = msg_list_sql.all()
        number = str(len(msg_list))
        data = []
        for msg in msg_list:
            item = {}
            item['msg_title'] = msg.msg_title
            item['id'] = msg.id
            data.append(item)
        return data, number
    except Exception as e:
        logging.debug(e)
        raise e


def get_all_send_message_with_limit(offset_data, page_size, search_data, sort, sortOrder):
    """
        获取所有的消息数据
        :return:
        """
    logging.info("get_all_send_message_with_limit")
    try:
        data = []
        user_id = str(session.get('user_id', 0))
        user = SysUser.query.filter_by(id=user_id).first()

        all_limit_msg = None
        if is_valid_date(search_data):
            all_limit_msg = SysMessage.query.filter(SysMessage.msg_date >= search_data + " 00:00:00",
                                                    SysMessage.msg_date < search_data + " 23:59:59").filter(
                SysMessage.msg_delete == 0, SysMessage.msg_sender == user.username)
        else:
            all_limit_msg = SysMessage.query.filter(
                SysMessage.msg_type == SysDict.dict_id,
                SysDict.dict_type == "sys_msg_type",
                or_(SysMessage.msg_title.like(search_data + '%'),
                    SysMessage.msg_type.like(search_data + '%'),
                    SysDict.dict_name.like('%' + search_data + '%')
                    )).filter(SysMessage.msg_delete == 0, SysMessage.msg_sender == user.username)
        limit_msg = all_limit_msg.order_by(
            sort_in_sysuser(sort, sortOrder)).offset(offset_data).limit(page_size).all()

        type_data = {}
        sys_dict = SysDict.query.filter(SysDict.dict_type == 'sys_msg_type', SysDict.del_flag == 0).all()
        for dict in sys_dict:
            type_data[dict.dict_id] = dict.dict_name

        for msg in limit_msg:
            item = {}
            item['msg_title'] = msg.msg_title
            item['msg_type'] = type_data.get(msg.msg_type)
            item['msg_date'] = msg.msg_date.strftime("%Y-%m-%d %H:%M:%S")
            item['msg_id'] = msg.msg_id
            item['id'] = msg.id
            data.append(item)

        return {'total': all_limit_msg.count(), 'rows': data}
    except Exception as e:
        logging.debug(e)
        raise e


def is_valid_date(strdate):
    """
    判断是否是一个有效的日期字符串
    :param strdate:
    :return:
    """
    logging.info("is_valid_date")
    try:
        if ":" in strdate:
            time.strptime(strdate, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(strdate, "%Y-%m-%d")
        return True
    except:
        return False


def get_all_received_message_with_limit(offset_data, page_size, search_data, sort, sortOrder):
    """
    获取所有的已收消息
    :param offset_data:
    :param page_size:
    :param search_data:
    :return:
    """
    try:
        data = []
        user_id = str(session.get('user_id', 0))

        type_data = {}
        sys_dict = SysDict.query.filter(SysDict.dict_type == 'sys_msg_type', SysDict.del_flag == 0).all()
        for dict in sys_dict:
            type_data[dict.dict_id] = dict.dict_name

        status_data = {}
        dict_read_status = SysDict.query.filter(SysDict.dict_type == 'sys_msg_read_state', SysDict.del_flag == 0).all()
        for dict in dict_read_status:
            status_data[dict.dict_name] = dict.dict_id

        all_limit_msg = None
        if is_valid_date(search_data):
            all_limit_msg = SysMessage.query.filter(SysMessage.msg_date >= search_data + " 00:00:00",
                                                    SysMessage.msg_date < search_data + " 23:59:59")
        else:

            all_limit_msg = SysMessage.query.filter(
                SysMessage.msg_receiver.like("%['" + user_id + "', '0', %"),
                SysMessage.msg_type == SysDict.dict_id,
                SysDict.dict_type == "sys_msg_type")

            if search_data:
                if search_data in status_data:
                    all_limit_msg = all_limit_msg.filter(
                        SysMessage.msg_receiver.like("%['" + user_id + "', '0', '" + status_data[search_data] + "'%")
                    )
                else:
                    all_limit_msg = all_limit_msg.filter(
                        or_(
                            SysMessage.msg_title.like('%' + search_data + '%'),
                            SysMessage.msg_type.like('%' + search_data + '%'),
                            SysDict.dict_name.like('%' + search_data + '%'),
                        ))

        limit_msg = all_limit_msg.order_by(sort_in_sysuser(sort, sortOrder)).offset(offset_data).limit(page_size).all()

        type_data = {}
        sys_dict = SysDict.query.filter(SysDict.dict_type == 'sys_msg_type', SysDict.del_flag == 0).all()
        for dict in sys_dict:
            type_data[dict.dict_id] = dict.dict_name

        for msg in limit_msg:
            item = {}
            item['msg_title'] = msg.msg_title
            item['msg_type'] = type_data.get(msg.msg_type)
            item['msg_date'] = msg.msg_date.strftime("%Y-%m-%d %H:%M:%S")
            item['msg_state'] = 1
            list_receiver = list(eval(msg.msg_receiver))
            for i in range(len(list_receiver)):
                if list_receiver[i][0] == user_id and list_receiver[i][2] == '0':
                    item['msg_state'] = 0

            item['msg_id'] = msg.msg_id
            item['id'] = msg.id
            data.append(item)

        return {'total': all_limit_msg.count(), 'rows': data}
    except Exception as e:
        logging.debug(e)
        raise e


def get_all_received_message_without_limit(user_id):
    """
    获取当前用户的所有消息
    :param id:
    :return:
    """
    all_msg = SysMessage.query.filter(
        SysMessage.msg_receiver.like("%['" + user_id + "', '0', %"),
        SysMessage.msg_type == SysDict.dict_id,
        SysDict.dict_type == "sys_msg_type").order_by(db.desc(SysMessage.msg_date)).all()
    data = []
    for msg in all_msg:
        item = {}
        item['msg_title'] = msg.msg_title
        item['msg_id'] = msg.msg_id
        item['msg_sender'] = msg.msg_sender
        item['msg_date'] = msg.msg_date.strftime("%Y-%m-%d %H:%M:%S")
        data.append(item)
    return data


def sort_in_sysuser(data, sortOrder):
    """
    判断排序条件
    :param data:
    :param sortOrder:
    :return:
    """
    logging.info('sort_in_sysuser')
    if sortOrder == 'asc':
        if data == 'msg_title':
            return SysMessage.msg_title.asc()
        elif data == 'msg_type':
            return SysMessage.msg_type.asc()
        elif data == 'msg_date':
            return SysMessage.msg_date.asc()
        elif data == 'msg_state':
            return SysMessage.msg_receiver.asc()
        else:
            return None
    else:
        if data == 'msg_title':
            return SysMessage.msg_title.desc()
        elif data == 'msg_type':
            return SysMessage.msg_type.desc()
        elif data == 'msg_date':
            return SysMessage.msg_date.desc()
        elif data == 'msg_state':
            return SysMessage.msg_receiver.desc()
        else:
            return SysMessage.msg_date.desc()


def get_the_msg_by_id(id):
    """
    通过id获取消息
    :param msg_id:
    :return:
    :return:
    """
    try:
        sys_msg = SysMessage.query.filter_by(id=id).first()
        if sys_msg is not None:
            return sys_msg
    except Exception as e:
        logging.debug(e)
        raise e


def get_the_msg_by_msg_id(msg_id):
    """
        通过msg_id获取消息
        :param msg_id:
        :return:
        :return:
        """
    try:
        sys_msg = SysMessage.query.filter_by(msg_id=msg_id).first()
        if sys_msg is not None:
            return sys_msg
    except Exception as e:
        logging.debug(e)
        raise e


def delete_the_send_msg(msg_id):
    """
    删除发送消息
    :param msg_id:
    :return:
    """
    try:
        update_by, update_time = get_update_time_and_user()
        sys_msg = get_the_msg_by_id(msg_id)
        SysMessage.update(sys_msg, msg_delete=1, update_by=update_by, update_time=update_time)
    except Exception as e:
        logging.debug(e)
        raise e


def delete_the_msg(msg_id):
    """
    删除接收的消息
    :param msg_id:
    :return:
    """
    try:
        user_id = session.get('user_id', 0)
        update_by, update_time = get_update_time_and_user()
        msg = get_the_msg_by_id(msg_id)
        if msg is not None:
            list_receiver = list(eval(msg.msg_receiver))
            for i in range(len(list_receiver)):

                if list_receiver[i][0] == str(user_id) and list_receiver[i][1] == '0':
                    user_name = list_receiver[i][0]
                    msg_read_state = list_receiver[i][2]
                    list_receiver.remove(list_receiver[i])
                    list_receiver.append([user_name, '1', msg_read_state])
                    break
            SysMessage.update(msg, msg_receiver=str(list_receiver), update_by=update_by, update_time=update_time)
    except Exception as e:
        logging.debug(e)
        raise e


def set_msg_read_state(id, user_id):
    """
    设置消息阅读状态
    :param id:
    :return:
    """
    try:
        update_by, update_time = get_update_time_and_user()
        msg = SysMessage.query.filter_by(id=id).first()
        if msg is not None:
            list_receiver = list(eval(msg.msg_receiver))
            for i in range(len(list_receiver)):
                if list_receiver[i][0] == user_id and list_receiver[i][2] == '0':
                    list_receiver.remove(list_receiver[i])
                    list_receiver.append([user_id, '0', '1'])
            SysMessage.update(msg, msg_receiver=str(list_receiver), update_by=update_by, update_time=update_time)
            # data, number = get_msg_not_read(user_id)
            # session['flash_number'] = number
            # session['flash_data'] = data
            # flash(data, number)
    except Exception as e:
        logging.debug(e)
        raise e


def get_update_time_and_user():
    """
    获取更新时间 & 更新者名称
    :return:
    """
    user_id = session.get("user_id", 0)
    sysuser = SysUser.query.filter_by(id=user_id).first()
    update_by = sysuser.username
    update_time = datetime.now()
    return update_by, update_time

#############逻辑操作区域结束###################
