# -*- coding: utf-8 -*-
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @version: python3.6
# @author: YinChengping
# @project: rich_salekit
# @software: PyCharm
# @file: forms.py
# @time: 2017/10/26 18:29
import re
from flask_wtf import Form
from flask import session, json
from wtforms import (SelectField, StringField, TextAreaField, PasswordField, HiddenField,
                     SelectMultipleField, FileField)
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from test.extensions import db
from stdnum import luhn
from test.sysadmin import permission_view
from test.sysadmin.models import SysDict, SysDictType, Rolelist, SysUser, SysOrg, SysUserRole, Permissionlist, \
    OrgStatus
import logging
class DictForm(Form):
    """字典表单"""
    dict_name = StringField('dict_name')
    dict_id = StringField('dict_id')
    dict_type = StringField('dict_type', validators=[DataRequired(message='字典类型不能为空')])
    description = StringField('description', validators=[DataRequired(message='描述不能为空')])
    sort = StringField('sort')
    remarks = StringField('remarks')
    del_flag = SelectField('del_flag')
    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(DictForm, self).__init__(*args, **kwargs)
        self.del_flag.choices = [('0', '正常'), ('1', '停用')]

    def validate(self, is_add, old_data, new_data):
        """Validate the form."""
        super(DictForm, self).validate()
        isError = True

        if not new_data['dict_name']:
            isError = False
            self.dict_name.errors.append('字典名不能为空！')
        if not new_data['dict_id']:
            isError = False
            self.dict_id.errors.append('字典id不能为空！')
        elif not re.match('^[0-9]*[1-9][0-9]*$', str(new_data['dict_id'])):
            self.dict_id.errors.append('字典id只能为正数！')
            isError = False

        if not new_data['sort']:
            isError = False
            self.sort.errors.append('排序不能为空! ')
        elif not re.match('^[0-9]*[1-9][0-9]*$', str(new_data['sort'])):
            self.sort.errors.append('序号只能为正数！')
            isError = False

        if not isError:
            return isError

        dict_name = SysDict.query.filter(SysDict.dict_name == new_data['dict_name'],
                                         SysDict.dict_type == new_data['dict_type']).first()
        dict_id = SysDict.query.filter(SysDict.dict_id == new_data['dict_id'],
                                       SysDict.dict_type == new_data['dict_type']).first()
        dict_sort = SysDict.query.filter(SysDict.sort == new_data['sort'],
                                         SysDict.dict_type == new_data['dict_type']).first()

        if is_add == 'add':

            if dict_name is not None:
                self.dict_name.errors.append('该字典已存在！')
                isError = False
            elif dict_id is not None:
                self.dict_id.errors.append('该id已存在！')
                isError = False
            elif dict_sort is not None:
                self.sort.errors.append('该序号已存在! ')
                isError = False
        elif is_add == 'update':
            if new_data['dict_name'] != old_data.get('dict_name') or new_data['dict_type'] != old_data.get(
                    'dict_type'):
                if dict_name is not None:
                    self.dict_name.errors.append('该字典已存在！')
                    isError = False

            if new_data['dict_id'] != old_data.get('dict_id'):
                if dict_id is not None:
                    self.dict_id.errors.append('该id已存在！')
                    isError = False

            if new_data['sort'] != old_data.get('sort'):
                if dict_sort is not None:
                    self.sort.errors.append('该序号已存在! ')
                    isError = False

        return isError


class PermissionForm(Form):
    """
    权限
    """
    parent_id = HiddenField('parent_id')
    name = StringField('name')
    url = StringField('url')
    status = SelectField('status')
    type = SelectField('type')
    icon = StringField('icon')
    desc = TextAreaField('desc')
    sort = StringField('sort')

    def __init__(self, id, *args, **kwargs):
        super(PermissionForm, self).__init__(*args, **kwargs)
        self.id = id
        self.permission_name = None
        self.type.choices = permission_view.get_choices_list(SysDictType.permission_type.value)
        self.status.choices = permission_view.get_choices_list(SysDictType.permission_status.value)

    def validate(self):
        super(PermissionForm, self).validate()

        if not self.data.get('parent_id'):
            self.parent_id.errors.append('权限层级不能为空')
            return False
        if not self.data.get('status'):
            self.status.errors.append('权限状态不能为空')
            return False
        if not self.data.get('type'):
            self.type.errors.append('权限类型不能为空')
            return False
        if not self.data.get('sort'):
            self.sort.errors.append('权限排序不能为空')
            return False
        else:
            data_sort = self.data.get('sort')
            if not data_sort.isdigit():
                self.sort.errors.append('排序类型需要为数字整数')
                return False
        if not self.data.get('name'):
            self.name.errors.append('权限名称不能为空')
            return False
        else:
            permission_name = self.data.get('name')
            if len(permission_name) > 255:
                self.name.errors.append('权限名称字数不能超过255个')
                return False
            permission = Permissionlist.query.filter(Permissionlist.name == permission_name,
                                                     Permissionlist.del_flag == 0).first()
            if permission:
                self.name.errors.append('权限名称已存在!')
                return False
        if not self.data.get('url'):
            self.url.errors.append('权限路径不能为空')
            return False
        else:
            url = self.data.get('url')
            if len(url) > 255:
                self.url.errors.append('权限路径字数不能超过255个')
                return False
        if self.data.get('desc'):
            desc = self.data.get('desc')
            if len(desc) > 255:
                self.desc.errors.append('备注字数不能超过255个')
                return False
        if self.data.get('icon'):
            icon = self.data.get('icon')
            if len(icon) > 255:
                self.icon.errors.append('图标字数超过限制')
                return False
        return True

    def check_update(self, update_data):
        super(PermissionForm, self).validate()

        if not update_data.get('parent_id'):
            self.parent_id.errors.append('权限层级不能为空')
            return False
        if not update_data.get('status'):
            self.status.errors.append('权限状态不能为空')
            return False
        if not update_data.get('type'):
            self.type.errors.append('权限类型不能为空')
            return False
        if not update_data.get('sort'):
            self.sort.errors.append('权限排序不能为空')
            return False
        else:
            data_sort = update_data.get('sort')
            if not data_sort.isdigit():
                self.sort.errors.append('排序类型需要为数字整数')
                return False
        if not update_data.get('name'):
            self.name.errors.append('权限名称不能为空')
            return False
        else:
            permission_name = update_data.get('name')
            if len(permission_name) > 255:
                self.name.errors.append('权限名称字数不能超过255个')
                return False
            permission = Permissionlist.query.filter_by(id=self.id).first()
            if not permission_name == permission.name:
                permission = Permissionlist.query.filter_by(name=permission_name, del_flag=0).first()
                if permission:
                    self.name.errors.append('权限名称已存在!')
                    return False
        if not update_data.get('url'):
            self.url.errors.append('权限路径不能为空')
            return False
        else:
            url = update_data.get('url')
            if len(url) > 255:
                self.url.errors.append('权限路径字数不能超过255个')
                return False
        if update_data.get('desc'):
            desc = update_data.get('desc')
            if len(desc) > 255:
                self.desc.errors.append('备注字数不能超过255个')
                return False
        if update_data.get('icon'):
            icon = update_data.get('icon')
            if len(icon) > 255:
                self.icon.errors.append('图标字数超过限制')
                return False
        return True


class UserForm(Form):
    username = StringField('username', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('password')
    repassword = PasswordField('repassword')
    name = StringField('name')
    email = StringField('email', validators=[DataRequired(message='邮箱地址不能为空'),
                                             Regexp('[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$',
                                                    message='请输入正确的邮箱地址')])
    mobile = StringField('mobile', validators=[DataRequired(message='手机号码不能为空'),
                                               Regexp(
                                                   '^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(17([0-9]))|(18[0-9]))\\d{8}$',
                                                   message='请输入正确的手机号码')])
    sex = SelectField('sex')
    is_active = SelectField('is_active')
    # role = SelectField('role')
    org = StringField('org')
    org_name = StringField('org_name')
    role = HiddenField('role')
    chat_code = StringField('chat_code')
    desc = TextAreaField('desc')
    image = HiddenField('image')
    open_id = StringField('open_id')
    address = StringField('address')
    flag = StringField('flag')

    def __init__(self, id, *args, **kwargs):
        """Create instance."""
        Form.__init__(self, *args, **kwargs)

        self.id = id
        self.is_hidden = True
        self.title_name = None
        self.sex.choices = [('-1', '--请选择性别--'), ('0', '女'), ('1', '男')]
        self.is_active.choices = [('-1', '--请选择状态--'), ('0', '停用'), ('1', '正常')]
        user_id_session = session.get('user_id', 0)
        # self.org.choices = [(org.org_id, org.org_name)
        #                     for org in self.get_all_org_by_user_id(user_id_session)]
        # self.org.choices = [('-1', '--请选择机构--')]
        # for org in self.get_all_org_by_user_id(user_id_session):
        #     self.org.choices.append((org.org_id, org.org_name))
        self.role.choices = [(str(role.id), role.name)
                             for role in self.get_all_role_by_org_id(user_id_session)]
        if self.id == '0':
            self.title_name = '新增用户信息'

        else:
            self.title_name = '编辑用户信息'
            self.is_hidden = False

    def init_data(self, id):
        obj = SysUser.query.filter_by(id=id).first()
        self.username.data = obj.username
        self.sex.data = obj.sex
        self.is_active.data = str(obj.is_active)
        self.org.data = obj.org_id
        self.name.data = obj.name
        self.email.data = obj.email
        self.password.data = obj.password
        self.repassword.data = obj.password
        self.mobile.data = obj.mobile
        self.sex.data = obj.sex
        self.desc.data = obj.desc
        self.open_id.data = obj.open_id
        if obj.avatar == None:
            self.image.data = 'default.png'
        else:
            self.image.data = obj.avatar
        self.chat_code.data = obj.chat_code
        self.is_active.data = str(obj.is_active)
        self.org.data = str(obj.org_id)
        # self.role.choices = [(str(role.id), role.name)
        #                      for role in self.get_all_role_by_org_id(id)]
        role = SysUserRole.query.filter_by(user_id=id).first()
        if role:
            self.role.data = str(role.role_id)

    def get_all_role_by_org_id(self, user_id):
        try:
            ret = db.session.query(Rolelist).filter(SysUser.id == user_id, Rolelist.org_id == SysUser.org_id,
                                                    Rolelist.name != '超级管理员').all()
            return ret
        except Exception as e:
            raise e

    def get_all_org_by_user_id(self, user_id):
        try:
            sys_org = db.session.query(SysOrg).filter(SysUser.org_id == SysOrg.org_id,
                                                      SysUser.id == user_id).first()
            if sys_org:
                return SysOrg.query.filter(SysOrg.org_code.like(sys_org.org_code + '%')).all()
        except Exception as e:
            raise e

    def validate(self):

        initial_validation = super(UserForm, self).validate()

        if not initial_validation:
            return False

        if self.id == '0':  # 新增校验
            # 判断用户名是否存在
            return self.check_add()
        else:
            return self.check_edit()

    def check_add(self):
        user = SysUser.query.filter_by(username=self.data.get('username')).first()
        if user:
            self.username.errors.append('用户名已存在！')
            return False

        if self.data.get('chat_code'):
            chat_code_user = SysUser.query.filter_by(chat_code=self.data.get('chat_code')).first()

            if chat_code_user:
                self.chat_code.errors.append('微信号已存在')
                return False

        # 判断手机号是否存在
        phone_user = SysUser.query.filter_by(mobile=self.data.get('mobile')).first()
        if phone_user:
            self.mobile.errors.append('手机号码已存在！')
            return False
            # 判断邮箱是否重复
        email_user = SysUser.query.filter_by(email=self.data.get('email')).first()
        if email_user:
            self.email.errors.append('邮箱已存在！')
            return False
        if not self.password.data:
            self.password.errors.append('密码不能为空')
            return False
        if not self.repassword:
            self.repassword.errors.append('确认密码不能为空')
            return False
        if self.repassword.data != self.password.data:
            self.password.errors.append('前后两次密码不一致')
            return False
        if self.org.data == '-1':
            self.org.errors.append('请选择机构')
            return False
        if self.role.data == '-1':
            self.role.errors.append('请选择角色')
            return False
        if self.is_active.data == '-1':
            self.is_active.errors.append('请选择状态')
            return False

        return True

    def check_edit(self):

        user = SysUser.query.filter_by(id=self.id).first()
        if not self.data.get('username') == user.username:
            user = SysUser.query.filter_by(username=self.data.get('username')).first()
            if user:
                self.username.errors.append('用户名已存在！')
                return False
        if not self.data.get('mobile') == user.mobile:
            phone_user = SysUser.query.filter_by(mobile=self.data.get('mobile')).first()
            if phone_user:
                self.moblie.errors.append('手机号码已存在！')
                return False
        if not self.data.get('email') == user.email:
            email_user = SysUser.query.filter_by(email=self.data.get('email')).first()
            if email_user:
                self.email.errors.append('邮箱已存在！')
                return False
        if self.data.get('chat_code') != '':
            if not self.data.get('chat_code') == user.chat_code:
                chat_code_user = SysUser.query.filter_by(chat_code=self.data.get('chat_code')).first()
                if chat_code_user:
                    self.chat_code.errors.append('微信号已存在')
                    return False
        if self.is_active.data == '-1':
            self.is_active.errors.append('请选择状态')
            return False
        if self.org.data == '-1':
            self.org.errors.append('请选择机构')
            return False
        if self.role.data == '-1':
            self.role.errors.append('请选择角色')
            return False
        return True


class RoleForm(Form):
    name = StringField('name', validators=[DataRequired(message='角色名不能为空')])
    desc = StringField('desc')  # TextAreaField('desc')
    # org_id = SelectField('org_id')
    org_id = StringField('org_id')

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RoleForm, self).__init__(*args, **kwargs)
        self.roleinfo = None
        if kwargs.get('manage', 0) == 1:
            pass
        else:
            id = session.get("user_id", 0)
            # self.org_id.choices = [(str(org.org_id), org.org_name) for org in self.get_all_org_by_user_id(id)]

    def get_all_org_by_user_id(self, user_id):
        try:
            sys_org = db.session.query(SysOrg).filter(SysUser.org_id == SysOrg.org_id,
                                                      SysUser.id == user_id).first()
            if sys_org:
                return SysOrg.query.filter(SysOrg.org_code.like(sys_org.org_code + '%'), SysOrg.status == '1').all()
        except Exception as e:
            raise e

    def init_data_edit(self, id):
        targetrole = Rolelist.query.filter_by(id=id).first()
        org_id = targetrole.org_id
        name = SysOrg.query.filter_by(org_id=org_id).first().org_name
        id = session.get("user_id", 0)
        self.org_id.choices = [(str(org_id), name)]
        self.org_id.data = name  # 默认第一个是这个

    def init_data_edit_new(self, id):
        targetrole = Rolelist.query.filter_by(id=id).first()
        org_id = targetrole.org_id
        name = SysOrg.query.filter_by(org_id=org_id).first().org_name
        self.name.data = targetrole.name
        self.desc.data = targetrole.description  # 默认第一个是这个
        id = session.get("user_id", 0)
        # self.org_id.choices = [(str(org.org_id), org.org_name) for org in self.get_all_org_by_user_id(id)]
        self.org_id.data = org_id  # 默认第一个是这个

    def validate_edit(self, id):
        try:
            res = super(RoleForm, self).validate()
            if not res:
                return False
            if self.name.data == "超级管理员":
                self.name.errors.append('不能用超级管理员命名！')
                return False
            obj = Rolelist.query.filter_by(org_id=self.org_id.data, name=self.name.data).first()
            if obj:
                if obj.id != id:
                    self.name.errors.append('此机构下已有这个角色')
                    return False
            return True
        except Exception as e:
            logging.error(e)
            return False

    def init_data(self, id):
        targetrole = Rolelist.query.filter_by(id=id).first()
        org_id = targetrole.org_id
        id = session.get("user_id", 0)
        # self.org_id.choices = [(str(org.org_id), org.org_name) for org in self.get_all_org_by_user_id(id)]
        self.org_id.data = org_id  # 默认第一个是这个

    def validate(self):
        """Validate the form."""
        initial_validation = super(RoleForm, self).validate()
        if not initial_validation:
            return False
        if self.name.data == "超级管理员":
            self.name.errors.append('不能用超级管理员命名！')
            return False
        self.roleinfo = Rolelist.query.filter_by(name=self.name.data, org_id=self.org_id.data, status="正常").first()
        if self.roleinfo:
            self.name.errors.append('该角色名已使用！')
            logging.info('该角色名已使用！')
            return False
        return True


class PasswordForm(Form):
    password = PasswordField('password', validators=[DataRequired(message='旧密码不能为空')])
    newpassword = PasswordField('password', validators=[DataRequired(message='新密码不能为空')])
    pernewpassword = PasswordField('password', validators=[DataRequired(message='第二次新密码不能为空'),
                                                           EqualTo(fieldname='newpassword', message='前后两次密码不一致')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(PasswordForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(PasswordForm, self).validate()
        if not initial_validation:
            return False

        user_id = session.get('user_id', 0)
        user = SysUser.query.filter_by(id=user_id).first()

        if not SysUser.check_password(user, self.password.data):
            self.password.errors.append('旧密码不正确')
            return False

        return True


class MessageForm(Form):
    title = StringField('title', validators=[DataRequired(message='标题不能为空')])
    content = TextAreaField('content')
    type = SelectField('type', validators=[DataRequired(message='消息类型不能为空')])
    receiver = SelectMultipleField('receiver', validators=[DataRequired(message='接收人不能为空！')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(MessageForm, self).__init__(*args, **kwargs)

        choices_data = []
        org_code = session.get('org_code', 0)
        list_user = SysUser.query.join(SysOrg, SysOrg.org_id == SysUser.org_id).filter(
            SysOrg.org_code.like(org_code + '%')).all()
        for user in list_user:
            choices_data.append((str(user.id), user.username))

        self.receiver.choices = choices_data

        type_data = []
        sys_dict = SysDict.query.filter(SysDict.dict_type == 'sys_msg_type', SysDict.del_flag == 0).all()
        for dict in sys_dict:
            type_data.append((dict.dict_id, dict.dict_name))
        self.type.choices = type_data

    def validate(self, data):
        """Validate the form."""
        super(MessageForm, self).validate()

        if not data['title']:
            return False
        if not data['content']:
            self.content.errors.append('内容不能为空！')
            return False

        # text 类型字段最大限制64K
        if len(data['content']) >= 65535:
            self.content.errors.append('内容大小超出64K限制！')
            return False
        if not data['type']:
            return False
        return True


class OrgForm(Form):
    org_id = StringField('机构ID')  # , validators=[DataRequired(message='商户ID不能为空')])
    org_code = StringField('机构编码')  # , validators=[DataRequired(message='商户ID不能为空')])
    org_name = StringField('机构名', validators=[DataRequired(message='商户名不能为空')])
    org_short = StringField('机构简介', validators=[DataRequired(message='机构简称不能为空')])  # # 机构简称
    org_type = SelectField('机构类型', validators=[DataRequired(message='机构类型不能为空')])  # 机构类型
    master = StringField('法人名称', validators=[DataRequired(message='法人名称不能为空')])  # 法人名称
    idcard_number = StringField('身份证号码', validators=[DataRequired(message='身份证不能为空'), Regexp(
        '^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$',
        message='请输入正确的身份证号码')])
    district = StringField('具体地址', validators=[DataRequired(message='具体地址不能为空')])  # 具体地址',
    bl_address = StringField('经营地址', validators=[DataRequired(message='经营地址不能为空')])  # 经营地址
    contact = StringField('联系人', validators=[DataRequired(message='联系人不能为空')])  # 联系人',
    tel = StringField('联系电话', validators=[DataRequired(message='联系电话不能为空'), Regexp(
        '((13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9]|17[0|1|2|3|4|5|6|7|8|9])\d{8})|((010|\d{3}|02[0-9])-\d{8})$',
        message='请输入正确的电话号码')])  # 联系电话',
    website = StringField('网址')  # '网址',
    mail = StringField('邮箱')
    parent_org = StringField('父机构ID')
    org_area = SelectField('机构所在区域编码/省')  # 机构所在区域编码
    area_city = HiddenField('市')
    area_district = HiddenField('区/县')
    def __init__(self, id=None, *args, **kwargs):
        """Create instance."""
        user_id = session.get('user_id', 0)
        super(OrgForm, self).__init__(*args, **kwargs)
        self.status_val = None
        self.org_id.data = None
        self.id = id
        self.org_type.choices = [(str(dict_type.dict_id), dict_type.dict_name) for dict_type in
                                 db.session.query(SysDict).filter(SysDict.dict_type == 'sys_org_type').all()]
        # self.mem_type_code.choices = [(str(business_type.dict_id), business_type.dict_name) for business_type in
        #                               db.session.query(SysDict).filter(SysDict.dict_type == 'sys_ business_type').all()]
        self.org_area.choices = [(str(area.dict_id), area.dict_name) for area in
                                 db.session.query(SysDict).filter(SysDict.dict_type == 'sys_area_type',
                                                                  SysDict.dict_id.like('%0000')).all()]

    def get_all_org_by_user_id(self, user_id):
        try:
            sys_org = db.session.query(SysOrg).filter(SysUser.org_id == SysOrg.org_id,
                                                      SysUser.id == user_id).first()
            if sys_org:
                return SysOrg.query.filter(SysOrg.org_code.like(sys_org.org_code + '%')).all()
        except Exception as e:
            raise e

    def validate(self, *args, **kwargs):
        """Validate the form."""
        id = kwargs.get('id', None)
        status_get = kwargs.get('val', None)
        process_id = kwargs.get('process_id', None)
        vali = kwargs.get('vali_first', None)
        if vali is not None:
            status_get = OrgStatus.add.value
        initial_validation = super(OrgForm, self).validate()
        if not initial_validation:
            return False

        if self.mail.data:
            match_res = re.search('[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', self.mail.data)
            if not match_res:
                self.mail.errors.append('请输入正确的邮箱地址')
                return False
        if self.website.data:
            web_match_res = re.search('^((https?|ftp|news|http):\/\/)?([a-z]([a-z0-9\-]*[\.。])+'
                                      '([a-z]{2}|aero|arpa|biz|com|coop|edu|gov|info|int|jobs|mil|museum|name|nato|net|org|pro|travel)|'
                                      '(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))'
                                      '(\/[a-z0-9_\-\.~]+)*(\/([a-z0-9_\-\.]*)(\?[a-z0-9+_\-\.%=&]*)?)?(#[a-z][a-z0-9_]*)?$',
                                      self.website.data)

            if not web_match_res:
                self.website.errors.append('请输入正确的网址')
                return False

        if status_get is not None:  # 从URL渠道过来的数据
            if status_get == OrgStatus.add.value:
                if not self.parent_org.data:
                    self.parent_org.errors.append('所属机构不能为空！')
                    return False
                name_org = SysOrg.query.filter_by(org_name=self.org_name.data).first()
                if name_org:
                    self.org_name.errors.append('机构名称已存在！')
                    return False
                moblie_org = SysOrg.query.filter_by(tel=self.tel.data).first()
                if moblie_org:
                    self.tel.errors.append('联系电话已存在！')
                    return False
                return True
            else:  # 机构编辑
                id = id
                name_org = SysOrg.query.filter_by(org_name=self.org_name.data).first()
                if name_org is not None:
                    if name_org.id != int(id):
                        self.org_name.errors.append('机构名称已存在！')
                        return False
                tel = SysOrg.query.filter_by(org_name=self.tel.data).first()
                if tel is not None:
                    if tel.id != int(id):
                        self.tel.errors.append('联系电话已存在！')
                        return False
                return  True
