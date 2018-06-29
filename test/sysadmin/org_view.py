#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/26 18:29
# @Author  :  黄平
# @Site    : www.rich-money.com
# @File    : org_view.py
# @Software: 富融钱通系统
# @Function: 机构管理模块
import base64
import os
import platform
import logging
from flask import Blueprint, render_template, session, request, json, redirect, url_for, jsonify
from flask_login import login_required
from sqlalchemy import or_, func
from test.settings import Config
from test.extensions import csrf_protect
from test.extensions import db
from test.responsecode import ResponseCode
from test.sysadmin import message_view
from test.sysadmin.models import SysDict, SysOrg, SysUser, Rolelist, SysUserRole, OrgStatus
from test.sysadmin.forms import OrgForm
from test.sysadmin.permission_required import per_required
import time
from datetime import datetime
import requests, random

blueprint = Blueprint('sysorg', __name__, url_prefix='/sysorg', static_folder='../static')


@blueprint.route('/org/get/list')
@per_required
def org_get_list():
    '''
    database加载
    :return:
    '''
    logging.info('org_get_list')
    res_data, list_len = get_org_list_by()
    req_data = {'total': list_len, 'rows': res_data}
    return json.dumps(req_data)


@blueprint.route('/org')
@per_required
def org():
    """机构管理界面"""
    logging.info('org')
    return render_template('sysadmin/sysorg/sysorg.html')


@blueprint.route('/edit/org/<id>/<is_merchant>', methods=['GET', 'POST'])
@per_required
def edit_org_url(id, is_merchant):
    """
    机构管理编辑查看
    :return:
    """
    logging.info('edit_org_url')
    org_form = OrgForm(id)
    if org_form.is_submitted():
        if org_form.validate(val=OrgStatus.edit.value, id=id):
            data = request.form  # 证件图片保存  ...
            save_org(org_form, id)  #
            if is_merchant == "1":
                return redirect(url_for('merchant_manage.merchant_manage'))
            return redirect(url_for('sysorg.org'))
        else:
            return render_template('sysadmin/sysorg/sysorg_edit.html', org_form=org_form)
    obj = SysOrg.query.filter_by(id=id).first()
    org_form = set_form_value(org_form, obj)
    return render_template('sysadmin/sysorg/sysorg_edit.html', org_form=org_form, is_merchant=is_merchant)


@csrf_protect.exempt
@blueprint.route('/org/delete/', methods=['GET', 'POST'])
@per_required
def role_delete():
    '''
      删除机构
    :return:
    '''
    logging.info('role_delete')
    id = int(request.args.get("id"))
    res = SysOrg.query.filter_by(id=id).first()
    SysOrg.update(res, status='2')

    # all_setting = MerchantPaySetting.query.filter(MerchantPaySetting.org_id == res.org_id,
    #                                               MerchantPaySetting.del_flag == 0).all()
    # for setting in all_setting:
    #     MerchantPaySetting.update(setting, del_flag=1)
    #
    # all_info = MerchantInfo.query.filter(MerchantInfo.org_id == res.org_id,
    #                                      MerchantInfo.del_flag == 0).all()
    # for info in all_info:
    #     MerchantInfo.update(info, del_flag=1)

    # SysOrg.delete(res)  # 机构下面用户也要做停用处理 ---||||
    # 发送操作消息
    message_view.add_option_message("删除机构 '" + res.org_name + "'")
    name_dict = {'code': ResponseCode.SUCCESS, 'desc': '机构删除成功!'}
    return json.dumps(name_dict)


@blueprint.route('/org/add', methods=['GET', 'POST'])
@per_required
def merchants_add():
    """
    机构新增界面
    :return:
    """
    logging.info('merchants_add')
    data = request.form  # 证件图片保存
    org_form = OrgForm(data)
    if org_form.is_submitted():
        if org_form.validate(val=OrgStatus.add.value):
            save_org(org_form, 0)  # 0为新增数据
            return redirect(url_for('sysorg.org'))
        else:
            return render_template('sysadmin/sysorg/sysorg_add.html', org_form=org_form)
    return render_template('sysadmin/sysorg/sysorg_add.html', org_form=org_form)


@blueprint.route('/to/get/org/list', methods=['GET'])
@login_required
def to_get_org_list():
    """
    获取所属机构列表
    :return:
    """
    logging.info('to_get_org_list')
    try:
        req_data = user_get_org()
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '获取成功!', 'data': req_data}
        return json.dumps(name_dict)
    except Exception as e:
        name_dict = {'code': ResponseCode.ERROR, 'desc': '获取失败!', 'data': []}
        return json.dumps(name_dict)


@blueprint.route('/to/get/org/pagine/list', methods=['GET'])
@login_required
def to_get_org_pagine_list():
    """
    获取所属机构列表(分页)
    :return:
    """
    logging.info('to_get_org_list')
    try:
        params = request.args
        name = params.get("name", '')
        page = int(params.get("page", 0))
        page_num = 50
        skip = (page - 1) * page_num
        data = dict()
        orglists, count = user_get_org_by_name_and_limit(name, skip, str(page_num))
        data["item"] = orglists
        data["count"] = count
        more = page * 50 < data["count"]
        data["more"] = more

        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '获取成功!', 'data': data}
        return jsonify(name_dict)
    except Exception as e:
        name_dict = {'code': ResponseCode.ERROR, 'desc': '获取失败!', 'data': []}
        return json.dumps(name_dict)


@csrf_protect.exempt
@blueprint.route('/org/changestatus/', methods=['GET', 'POST'])
@per_required
def org_changestatus():
    """
    机构状态改变 停用后当前机构下面的用户也会停用
    :return:
    """
    logging.info('org_changestatus')
    try:
        logging.info(org_changestatus)
        id = int(request.args.get("id"))
        res = SysOrg.query.filter_by(id=id).first()
        if res.org_code == "0001":  # 0001的编码是最高级机构
            name_dict = {'code': ResponseCode.ERROR, 'desc': '该机构不能被停用!'}
            return json.dumps(name_dict)
        user_id = session.get("user_id", 0)
        user = SysUser.query.filter_by(id=user_id).first()
        if res.status == "1":  # 1正常
            objlist = SysOrg.query.filter(SysOrg.org_code.like(res.org_code + '%')).all()
            for item in objlist:
                SysOrg.update(item, status="0", update_by=user.username, update_date=datetime.now())
                user_list = SysUser.query.filter_by(org_id=item.org_id).all()
                for user1 in user_list:
                    SysUser.update(user1, is_active=0, update_time=datetime.now(), update_by=user.username)
        else:
            SysOrg.update(res, status="1", update_by=user.username, update_date=datetime.now())
            itemobj = SysUser.query.filter_by(org_id=res.org_id).all()
            for item in itemobj:
                SysUser.update(item, is_active=1, update_time=datetime.now(), update_by=user.username)

        # 发送操作消息
        message_view.add_option_message("更新机构 '" + res.org_name + "' 的状态")
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '状态更新成功!'}
        return json.dumps(name_dict)
    except Exception as e:
        logging.warning(e)
        raise e


@blueprint.route('/get/mcc/list', methods=['GET'])
@login_required
def to_get_mcc_list():
    """
    获取经营类别列表
    :return:
    """
    logging.info('to_get_mcc_list')
    try:
        data = []
        sys_dict_list = query_business_type_list()
        for item in sys_dict_list:
            dict = {}
            dict['id'] = item.dict_id
            dict['value'] = item.dict_name
            data.append(dict)
        name_dict = {'code': ResponseCode.SUCCESS, 'desc': '获取成功!', 'data': data}
        return json.dumps(name_dict)
    except Exception as e:
        name_dict = {'code': ResponseCode.ERROR, 'desc': '获取失败!', 'data': []}
        return json.dumps(name_dict)


def user_get_org():
    """
    获取机构名称列表:ycp
    :return:
    """
    logging.info('user_get_org')
    try:
        user_id = session.get('user_id', 0)
        sys_org = db.session.query(SysOrg).filter(SysOrg.org_id == SysUser.org_id, SysUser.id == user_id).first()
        if sys_org:
            org_list = SysOrg.query.filter(SysOrg.org_code.like(sys_org.org_code + '%')).all()
            org_data_list = []
            for org in org_list:
                dict = {}
                dict['id'] = org.org_id
                dict['value'] = org.org_name
                org_data_list.append(dict)
            return org_data_list
    except Exception as e:
        logging.debug(e)
        raise e


def user_get_org_by_name_and_limit(select_val, page_num, page_size):
    """
    获取机构名称列表:ycp
    :return:
    """
    logging.info('user_get_org_by_name_and_limit')
    try:
        user_id = session.get('user_id', 0)
        sys_org = db.session.query(SysOrg).filter(SysOrg.org_id == SysUser.org_id, SysUser.id == user_id).first()
        if sys_org:
            org_list = SysOrg.query.filter(SysOrg.org_code.like(sys_org.org_code + '%')). \
                filter(or_(SysOrg.org_code.like('%' + select_val + '%'),
                           SysOrg.org_name.like('%' + select_val + '%')))
            org_item_list = org_list.offset(page_num).limit(page_size).all()
            org_item_count = org_list.count()
            org_data_list = [{"id": org.org_id, "org_code": org.org_code, "value": org.org_name} for org in
                             org_item_list]
            return org_data_list, org_item_count
    except Exception as e:
        logging.debug(e)
        raise e


def get_org_list_data(user_id):
    """
    根据用户ID获取机构列表数据
    :return:
    """
    logging.info('get_org_list_data')
    try:
        sys_org = db.session.query(SysOrg).filter(SysOrg.org_id == SysUser.org_id, SysUser.id == user_id).first()
        if sys_org:
            org_list = SysOrg.query.filter(SysOrg.org_code.like(sys_org.org_code + '%')).all()
            org_data_list = []
            for sys_org in org_list:
                data = [
                    sys_org.id,
                    sys_org.id,
                    sys_org.org_name,
                    sys_org.org_id,
                    sys_org.audit,
                    sys_org.status,
                    sys_org.id
                ]
                org_data_list.append(data)
            return org_data_list
    except Exception as e:
        logging.debug(e)
        raise e


def query_business_type_list():
    """
    获取经营类别
    :param :
    :return:
    """
    logging.info('query_business_type_list')
    try:
        return SysDict.query.filter_by(dict_type='sys_ business_type').all()
    except Exception as e:
        logging.debug(e)
        raise e


# def add_org(*args, **kwargs):
#     """
#     动态表单增加数据时高用方法
#     :param args:
#     :param kwargs:
#     :return:
#     """
#     logging.info('流程任务调用方法add_org')
#     org_form = kwargs.get('forms', None)
#     process_id = kwargs.get('process_id', None)
#     # 如果是返回来的新增 就要变成是编辑的状态了
#     from test.merchant.merchant_audit_view import check_skip_back
#     from test.workflow.models import FlowTaskProcess, FlowTaskProcessFlag
#     tmp_ = check_skip_back(process_id)
#     if tmp_:
#         # 找到上一个节点对象的输出数据  流程每个节点前后数据有关联 商户注册在第一步执行
#         now_check = FlowTaskProcess.query.filter_by(process_id=process_id,
#                                                     flag=FlowTaskProcessFlag.process_pending.value).first()
#         dicts = json.loads(now_check.output_data)
#         id_num = dicts['info']['id']  # 数据格式化已定义好 每个数据相对应
#         obj = save_org(org_form, id_num)  # id为传进去的值
#         temp = FlowTaskProcess.query.filter(FlowTaskProcess.process_id == process_id).all()
#         for item in temp:
#             FlowTaskProcess.update(item, biz_name=obj.org_name)
#         return obj
#     else:
#         if org_form is None:
#             return None
#         obj = save_org(org_form, 0)  # 0为新增机构
#         obj = SysOrg.update(obj, status='0')  # 商户注册时给停用状态 待审核全部通过后再把状态改为正常
#         return obj
#
#
# def edit_org(*args, **kwargs):
#     """
#     动态表单编辑数据调用方法
#     :param args:
#     :param kwargs:
#     :return:
#     """
#     org_form = kwargs.get('forms', None)
#     process_id = kwargs.get('process_id', None)
#     from test.merchant.merchant_audit_view import get_now_check_task
#     from test.utils import import_class
#     from test.workflow.models import FlowTaskProcess
#     # 找到上一个节点对象的输出数据  流程每个节点前后数据有关联
#     now_check, last_obj = get_now_check_task(process_id)  # 调用找节点对象API
#     logging.info(now_check)
#     logging.info(last_obj)
#     dicts = json.loads(last_obj.output_data)
#     id_num = dicts['info']['id']  # 数据格式化已定义好 每个数据相对应
#     data_model = import_class(dicts['model'])  # 引入MODEL
#     mod_ = data_model()  # 初始化模型
#     resobj = mod_.query.filter_by(id=int(id_num)).first()
#     id = resobj.id  # 从任务进程ID找到任务目标任务biz_id-->生成目标对象-->对象ID
#     if org_form is None:
#         return None
#     obj = save_org(org_form, id)  # id为传进去的值
#     temp = FlowTaskProcess.query.filter(FlowTaskProcess.process_id == process_id).all()
#     for item in temp:
#         FlowTaskProcess.update(item, biz_name=obj.org_name)
#     return obj


def save_org(org_form, id):
    '''
    保存编辑后的内容
    :param org_form:
    :param id:
    :return:
    '''
    logging.info('save_org')
    try:
        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()  # 操作用户
        org_longitude, org_latitude = geocodeB(org_form.bl_address.data)
        if (id == 0):
            # 平台自动帮生成机构ID 机构编码 机构等级
            org_code, org_grade = create_org_code(org_form.parent_org.data)
            org_id = create_org_id()
            parent_org = org_form.parent_org.data
            org_code, org_grade = create_org_code(parent_org)  # 机构编码和机构等级
            new_org = SysOrg.create(
                org_id=org_id,  # 机构ID   -------------------- 平台帮生成
                org_grade=org_grade,  # 机构等级-------------- 平台帮生成
                org_code=org_code,  # ---机构编码----------- 平台帮生成
                org_name=org_form.org_name.data,  # 机构名称
                org_short=org_form.org_short.data,  # 机构简称
                status = 1,
                # mem_type_code=org_form.mem_type_code.data or '',  # -  -
                org_type=org_form.org_type.data,  # 机构类型
                latitude=org_latitude,  #
                longitude=org_longitude,  #
                org_area=org_form.area_district.data,  ## 机构所在区域编码
                # sign_funds=org_form.sign_funds.data,  #
                master=org_form.master.data,  #
                idcard_number=org_form.idcard_number.data,  #
                district=org_form.district.data,  #
                bl_address=org_form.bl_address.data,  #
                contact=org_form.contact.data,  #
                tel=org_form.tel.data,  #
                mail=org_form.mail.data,  #
                website=org_form.website.data,  #
                create_date=datetime.now(),
                create_by=user.username,
            )

            # 发送操作消息
            message_view.add_option_message("新增机构 '" + org_form.org_name.data + "'")
            #  新增机构，默认给机构添加一个普通管理员角色
            role_name = ['普通管理员', '游客']
            for item in role_name:
                create_role_for_org(item, org_id)
            return new_org
            # return None
        obj = SysOrg.query.filter_by(id=id).first()
        data = request.form.to_dict()
        if obj.org_code[:-4] and not obj.org_code[:-4] == org_form.parent_org.data:
            org_code, org_grade = create_org_code(org_form.parent_org.data)
        else:
            org_code = obj.org_code
            org_grade = obj.org_grade
        updata_res = SysOrg.update(obj,
                                   # org_id=org_form.org_id.data,
                                   org_name=org_form.org_name.data,
                                   org_code=org_code,
                                   org_short=org_form.org_short.data,
                                   org_grade=org_grade,
                                   org_type=org_form.org_type.data,
                                   latitude=org_latitude,
                                   longitude=org_longitude,
                                   # mem_type_code=org_form.mem_type_code.data,
                                   org_area=org_form.area_district.data,
                                   # sign_funds=org_form.sign_funds.data,
                                   master=org_form.master.data,
                                   idcard_number=org_form.idcard_number.data,
                                   district=org_form.district.data,
                                   bl_address=org_form.bl_address.data,
                                   contact=org_form.contact.data,
                                   tel=org_form.tel.data,
                                   mail=org_form.mail.data,
                                   website=org_form.website.data,
                                   update_by=user.username,
                                   update_date=datetime.now(),
                                   )

        # 发送操作消息
        message_view.add_option_message("更新机构 '" + obj.org_name + "' 的信息")
        return updata_res
    except Exception as e:
        logging.debug(e)
        raise e


def get_org_list_by():
    """
    获取机构列表数据 org_id
    :param  org_id :
    :return:
    """
    logging.info('get_org_list_by')
    try:
        user_id = session.get('user_id', 0)
        page_number = request.args.get('pageNumber')
        page_size = request.args.get('pageSize')
        offset_data = (int(page_number))
        search_data = request.args.get('searchData')
        sort = request.args.get('sort')
        sortOrder = request.args.get('sortOrder')
        if search_data:
            offset_data = 0
        else:
            search_data = ''
        res_data = []
        role = db.session.query(Rolelist).filter(Rolelist.id == SysUserRole.role_id,
                                                 SysUserRole.user_id == user_id).first()
        if role and role.name == '超级管理员':
            listdata = SysOrg.query.filter(
                SysOrg.status.in_(('0', '1')),
                or_(SysOrg.org_name.like('%' + search_data + '%'), SysOrg.tel.like('%' + search_data + '%'),
                    SysOrg.org_code.like('%' + search_data + '%'), SysOrg.org_id.like('%' + search_data + '%'),
                    SysOrg.status.like('%' + search_data + '%'))).order_by(sort_in_sysuser(sort, sortOrder)).offset(
                offset_data).limit(page_size).all()
            list_len = SysOrg.query.filter(
                SysOrg.status.in_(('0', '1')),
                or_(SysOrg.org_name.like('%' + search_data + '%'), SysOrg.tel.like('%' + search_data + '%'),
                    SysOrg.org_code.like('%' + search_data + '%'), SysOrg.org_id.like('%' + search_data + '%'),
                    SysOrg.status.like('%' + search_data + '%'))).count()
        else:
            org = db.session.query(SysOrg).filter(SysOrg.org_id == SysUser.org_id, SysUser.id == user_id).first()
            if org:
                listdata = SysOrg.query.filter(SysOrg.org_code.like('%' + org.org_code + '%'),
                                               SysOrg.status.in_(('0', '1')),
                                               or_(SysOrg.org_name.like('%' + search_data + '%'),
                                                   SysOrg.tel.like('%' + search_data + '%'),
                                                   SysOrg.org_code.like('%' + search_data + '%'),
                                                   SysOrg.org_id.like('%' + search_data + '%'),
                                                   SysOrg.status.like('%' + search_data + '%'))).order_by(
                    sort_in_sysuser(sort, sortOrder)).offset(
                    offset_data).limit(page_size).all()
                list_len = SysOrg.query.filter(SysOrg.org_code.like('%' + org.org_code + '%'),
                                               SysOrg.status.in_(('0', '1')),
                                               or_(SysOrg.org_name.like('%' + search_data + '%'),
                                                   SysOrg.tel.like('%' + search_data + '%'),
                                                   SysOrg.org_code.like('%' + search_data + '%'),
                                                   SysOrg.org_id.like('%' + search_data + '%'),
                                                   SysOrg.status.like('%' + search_data + '%'))).count()
        for role in listdata:
            dict = {}
            dict['id'] = role.id,
            dict['org_name'] = role.org_name,
            dict['tel'] = role.tel,
            dict['org_code'] = role.org_code,
            dict['org_id'] = role.org_id,
            dict['status'] = statustype(role.status),
            res_data.append(dict)
        return res_data, list_len
    except Exception as e:
        logging.debug(e)
        raise e


def statustype(type):
    if type == '1':
        return '正常'
    else:
        return '停用'


def sort_in_sysuser(sort, sortOrder):
    """

    :param sort:
    :param sortOrder:
    :return:
    """
    logging.info('sort_in_sysuser')
    if sortOrder == 'asc':
        if sort == 'org_name':
            return SysOrg.org_name.asc()
        elif sort == 'tel':
            return SysOrg.tel.asc()
        elif sort == 'org_id':
            return SysOrg.org_id.asc()
        elif sort == 'org_code':
            return SysOrg.org_code.asc()
        elif sort == 'status':
            return SysOrg.status.asc()
        else:
            return ''
    else:
        if sort == 'org_name':
            return SysOrg.org_name.desc()
        elif sort == 'tel':
            return SysOrg.tel.desc()
        elif sort == 'org_id':
            return SysOrg.org_id.desc()
        elif sort == 'org_code':
            return SysOrg.org_code.desc()
        elif sort == 'status':
            return SysOrg.status.desc()
        else:
            return ''


def create_org_id():
    """
    生成机构唯一标识----org_id
    :return:
    """
    logging.info('create_org_id')
    return "G" + str(int(time.time()))


def create_org_code(org_code):
    """
    根据所属机构org_code，生成机构编码
    :return:
    """
    logging.info('create_org_code')
    try:
        sys_org = SysOrg.query.filter_by(org_code=org_code).first()
        if sys_org:
            new_leve_org_code_length = len(sys_org.org_code) + 4
            query_org = SysOrg.query.filter(SysOrg.org_code.like(org_code + '%'),
                                            func.length(SysOrg.org_code) == new_leve_org_code_length).order_by(
                -SysOrg.org_code).first()
            if query_org:
                org_code = "000" + str(int(query_org.org_code) + 1)
            else:
                org_code = sys_org.org_code + '0001'

            # leve = len(org_code) / 4 + 1
            leve = len(org_code) / 4

            return org_code, leve

    except Exception as e:
        logging.debug(e)
        raise e


def set_form_value(org_form, obj):
    logging.info('set_form_value')
    try:
        if not obj.org_area:
            obj.org_area = '000000'

        area_city_code = obj.org_area[:4] + '00'
        area_province_code = obj.org_area[:2] + '0000'
        city_dict = SysDict.query.filter_by(dict_id=area_city_code, dict_type='sys_area_type').first()
        province_dict = SysDict.query.filter_by(dict_id=area_province_code, dict_type='sys_area_type').first()

        org_form.org_id.data = obj.org_id  # 机构ID
        org_form.org_code.data = obj.org_code  # 机构编码
        if obj.org_code[:-4]:
            org_form.parent_org.data = obj.org_code[:-4]
        else:
            org_form.parent_org.data = '0000'
        org_form.org_name.data = obj.org_name  # 机构名称
        # org_form.org_code.data= obj.org_code #
        org_form.org_short.data = obj.org_short  # 机构简称
        # org_form.org_category.data= obj.org_category#
        org_form.org_type.data = obj.org_type  # 机构类型
        # org_form.latitude.data= obj.latitude #
        # org_form.longitude.data= obj.longitude#
        # org_form.status.data= obj.status#
        # org_form.mem_type_code.data = obj.mem_type_code  #

        org_form.area_district.data = obj.org_area  ## 机构所在区域编码
        org_form.org_area.data = province_dict.dict_id if province_dict else None
        org_form.area_city.data = city_dict.dict_id if city_dict else None
        # org_form.sign_funds.data = obj.sign_funds  #
        org_form.master.data = obj.master  #
        org_form.idcard_number.data = obj.idcard_number  #
        org_form.district.data = obj.district  #
        org_form.bl_address.data = obj.bl_address  #
        org_form.contact.data = obj.contact  #
        org_form.tel.data = obj.tel  #
        org_form.mail.data = obj.mail  #
        # org_form.user.username= obj.user #
        org_form.website.data = obj.website
        return org_form
    except Exception as e:
        logging.debug(e)
        raise e


def save_image(img, org_id, img_name):
    """
            保存图片到本地目录
        :return:
        """
    logging.info('save_image')
    try:
        if img is not None and 'data' in img:
            img = img.split(',')[1]
            imgdata = base64.b64decode(img)
            current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            CURRENT_SYSTEM = platform.system()
            if CURRENT_SYSTEM == 'Windows':
                image_path = current_path + '\\static\\images\\org\\' + org_id + '\\'
            else:
                image_path = current_path + '/static/images/org/' + org_id + '/'
            if not os.path.exists(image_path):
                os.mkdir(image_path)
            file = open(image_path + img_name + '.png', 'wb+')
            file.write(imgdata)
            file.close()
            image_url = org_id + '/' + img_name + '.png'
        else:
            image_url = 'default.png'
        return image_url
    except Exception as e:
        logging.debug(e)
        raise e


def updata_save_image(data, obj, img_name, org_id):
    """
    更新图片
    :param data:
    :param obj:
    :return:
    """
    logging.info('updata_save_image')
    try:
        image_list = data.get(img_name)
        if image_list:
            if 'data' in image_list:
                return save_image(image_list, org_id, img_name+get_random_num())
            else:
                if img_name == 'bl_img':
                    return obj.bl_img if obj.bl_img else 'default.png'
                elif img_name == 'door_img':
                    return obj.door_img if obj.door_img else 'default.png'
                elif img_name == 'cashier_img':
                    return obj.cashier_img if obj.cashier_img else 'default.png'
                elif img_name == 'card_opposite_img':
                    return obj.card_opposite_img if obj.card_opposite_img else 'default.png'
                elif img_name == 'card_correct_img':
                    return obj.card_correct_img if obj.card_correct_img else 'default.png'
                elif img_name == 'cert_correct_img':
                    return obj.cert_correct_img if obj.cert_correct_img else 'default.png'
                elif img_name == 'cert_opposite_img':
                    return obj.cert_opposite_img if obj.cert_opposite_img else 'default.png'
                elif img_name == 'authorization_img':
                    return obj.authorization_img if obj.authorization_img else 'default.png'
        else:
            return 'default.png'
    except Exception as e:
        logging.debug(e)
        raise e


def create_role_for_org(role_name, orgid):
    """
    为新增机构添加一个普通管理员角色
    :param role_name:
    :param org_id:
    :return:
    """
    logging.info('create_role_for_org:%s' + orgid)
    try:
        user_name = session.get('user_name', 0)

    except Exception as e:
        logging.debug(e)
        raise e


def get_save_time_str():
    return str(int(round(time.time() * 1000)))


def geocodeB(address):
    try:
        base = Config.BAIDU_MAP_URL + "/?address=" + address + "&output=json&ak=iN6oMgMYyneB2PVqk40K5qCF9efLTFvj"
        response = requests.get(base)
        answer = response.json()
        return answer['result']['location']['lng'], answer['result']['location']['lat']
    except Exception as e:
        return '', ''


@blueprint.route('/org/geocodeB/', methods=['GET'])
def update_geocodeB():
    '''
      更新机构经纬度
    :return:
    '''
    logging.info('update_geocodeB')
    org_lists = SysOrg.query.filter_by(mem_type_code=270).all()
    print(org_lists)
    for orgs in org_lists:
        org_lng_lat = str(geocodeB(orgs.bl_address))
        lng_lat = org_lng_lat.split(',')
        lng = lng_lat[0].replace('(', '').replace(')', '').replace('\'', '').replace(' ', '')
        lat = lng_lat[1].replace('(', '').replace(')', '').replace('\'', '').replace(' ', '')
        print(lng)
        print(lat)
        SysOrg.update(orgs, latitude=lat, longitude=lng)

    name_dict = {'code': ResponseCode.SUCCESS, 'desc': '更新成功!'}
    return json.dumps(name_dict)


def get_random_num():
    """
    获取三位随机数
    :return:
    by wangzhouyang
    """
    logging.info("get_random_num")
    temp = '_'
    for i in range(3):
        res = random.randint(0, 9)
        temp = temp + str(res)
    return temp
