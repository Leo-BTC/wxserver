#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/31 下午5:15
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : models.py
# @Software: 富融钱通
# @Function: 系统管理模块-数据模型

import logging
import enum
import datetime as dt
from flask_login import UserMixin
from test.database import SurrogatePK, Model, db
from sqlalchemy import Column, String, Integer, DateTime, text,ForeignKey, UniqueConstraint, Index
from flask import session
from datetime import datetime
from test.extensions import bcrypt
from test.sysadmin import permission_view


class PermissionType(enum.Enum):
    """
    权限类型
    """
    confine = 0  # 限制权限
    default = 1  # 默认权限
    menu = 2  # 菜单权限
    operation = 3  # 操作权限


class PermissionStatus(enum.Enum):
    """
    权限状态
    """
    normal = 0  # 正常  #  add
    disable = 1  # 停用 #  edit


class OrgStatus(enum.Enum):
    """
    机构新增，编辑状态
    """
    add = 1  # add
    edit = 2  # #  edit


class SysDictType(enum.Enum):
    """
    系统字典表类型
    """
    sys_org_type = 'sys_org_type'  # 机构类型
    sys_org_grade = 'sys_org_grade'  # 机构等级
    sys_data_scope = 'sys_data_scope'  # 数据范围
    sys_tran_status = 'sys_tran_status'  # 交易类型
    sys_tran_appl = 'sys_tran_appl'  # 交易类型应用标识
    sys_audit_status = 'sys_audit_status'  # 审核状态
    sys_channel = 'sys_channel'  # 平台通道
    sys_chanel_code = 'sys_chanel_code'  # 支付通道
    sys_business_type = 'sys_ business_type'  # 经营类型
    permission_type = 'permission_type'  # 权限类型
    permission_status = 'permission_status'  # 权限状态


class Permissionlist(SurrogatePK, Model):
    __tablename__ = 'permissionlist'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)  # 权限名
    url = Column(String(64), nullable=False)  # url地址
    type = Column(Integer, nullable=False)  # 权限类型
    parent_id = Column(Integer, nullable=False)  # 父类id
    create_time = Column(DateTime)  # 创建时间
    update_time = Column(DateTime)  # 更新时间
    create_by = Column(String(64))  # 创建人
    update_by = Column(String(64))  # 修改人
    status = Column(Integer, nullable=False)  # 状态
    desc = Column(String(255))  # 备注
    del_flag = Column(Integer, nullable=False)  # 删除标识
    icon = Column(String(64))  # 图标
    sort = Column(Integer, nullable=False)  # 排序


class Rolelist(SurrogatePK, Model):
    __tablename__ = 'rolelist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))  # 角色名
    role_type = Column(String(16))  # 角色类型1: 平台默认角色, 0: 机构定义角色
    org_id = Column(String(64), index=True, nullable=True)  # 机构id
    create_by = Column(String(64))  # 创建人
    update_by = Column(String(64))  # 修改人
    create_time = Column(DateTime)  # 创建时间
    update_time = Column(DateTime)  # 修改时间
    owners = Column(String(64))  # ---?   用户id 默认空可以看全部数据;根据用户id过滤用户的数据
    description = Column(String(255))  # 描述
    status = Column(String(16), default="正常")  # 状态

    __table_args__ = (
        UniqueConstraint('id', 'org_id', name='uix_id_name'),  # 联合唯一索引
        Index('ix_id_name', 'id', 'org_id'),  # 联合索引
    )

    def __init__(self, **kwargs):
        """Create instance."""
        Model.__init__(self, **kwargs)
        id = session.get("user_id", 0)
        sysuser = SysUser.query.filter_by(id=id).first()
        if sysuser:
            self.create_by = sysuser.username
            self.create_time = datetime.now()
            if (int(id) == 2):  # 2   -- >  admin
                self.role_type = "平台创建"
            else:
                self.role_type = "机构创建"


class SysOrg(SurrogatePK, Model):
    __tablename__ = 'sys_org'

    id = Column(Integer, primary_key=True)
    org_id = Column(String(64))  # 机构ID，唯一字段，以时间戳',
    org_name = Column(String(64))  # 机构名称
    org_short = Column(String(64))  # 机构简称
    org_grade = Column(String(64))  # 机构等级',
    org_type = Column(String(64))  # 机构类型
    org_code = Column(String(64))  # 机构编码
    latitude = Column(String(64))  # '纬度',
    longitude = Column(String(64))  # '经度'
    status = Column(String(16), default="0")  # 状态 1:正常 0:停用 2：已删除
    mem_type_code = Column(String(16))  # 经营类型编码
    org_area = Column(String(16))  # 机构所在区域编码
    sign_funds = Column(String(64))  # 注册资金
    master = Column(String(64))  # 法人名称
    idcard_number = Column(String(64))  # 身份证号码
    district = Column(String(64))  # 具体地址',
    bank_address = Column(String(64))  # 开户银行地址
    bl_address = Column(String(64))  # 经营地址
    contact = Column(String(64))  # 联系人',
    mobile = Column(String(64))  # 银行绑定手机号码',
    tel = Column(String(64))  # 联系电话',
    mail = Column(String(64))  # '邮箱',

    bl_img = Column(String(64))  # 营业执照照片',
    door_img = Column(String(64))  # 门头照',
    cashier_img = Column(String(64))  # 收银台照',
    card_opposite_img = Column(String(64))  # 银行卡背面照',
    card_correct_img = Column(String(64))  # 银行卡正面照',
    authorization_img = Column(String(64))  # 授权书照',
    cert_correct_img = Column(String(64))  # 身份证正面照',
    cert_opposite_img = Column(String(64))  # 身份证背面照',

    bank_card_type = Column(String(64))  # '银行卡类型（1：结算卡）',
    bank_account = Column(String(64))  # '银行卡账号',
    bank_name = Column(String(64))  # '银行名',
    bank_owner = Column(String(64))  # '银行卡用户名',

    create_by = Column(String(64))  #
    create_date = Column(DateTime)  #
    update_by = Column(String(64))  #
    update_date = Column(DateTime)  #
    website = Column(String(64))  # '网址',
    remarks = Column(String(255))  # '备注',
    qcode_img = Column(String(255))
    mer_info = Column(String(1024))
    # audit = Column(String(64))  # 是否审核（0：是；1：否）',
    # parent_org_id = Column(String(64))  # 父机构ID

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(SysOrg, self).__init__(*args, **kwargs)

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


class SysRolePermissionlist(SurrogatePK, Model):
    __tablename__ = 'sys_role_permissionlist'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer)  # 角色ID
    permissionlist_id = Column(Integer)  # 权限ID
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    create_by = Column(String(64))
    update_by = Column(String(64))

    def __init__(self, **kwargs):
        """Create instance."""
        Model.__init__(self, **kwargs)
        id = session.get("user_id", 0)
        sysuser = SysUser.query.filter_by(id=id).first()
        self.create_by = sysuser.username
        self.create_time = datetime.now()


class SysUser(UserMixin, SurrogatePK, Model):
    """
    用户管理
    """
    __tablename__ = 'sys_user'

    id = Column(Integer, primary_key=True)
    password = Column(String(255))
    last_login = Column(DateTime)
    email = Column(String(64))
    username = Column(String(64))
    name = Column(String(64))
    is_active = Column(Integer, server_default=text("'1'"))  # 是否活跃用户（1：正常；0：停用）
    sex = Column(Integer, server_default=text("'0'"))  # 性别 (1男 0女)
    mobile = Column(String(16))
    desc = Column(String(255))  # 简介
    avatar = Column(String(64))  # 头像路径
    type = Column(Integer)  # 用户类型
    create_by = Column(String(64))
    update_by = Column(String(64))
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    chat_code = Column(String(64))  # 微信号
    open_id = Column(String(64))  # open_id
    org_id = Column(String(64))

    def __init__(self, username, password=None, **kwargs):
        """Create instance."""
        Model.__init__(self, username=username, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        logging.info('set_password')
        self.password = bcrypt.generate_password_hash(password)
        return self.password

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def can(self, path_url):
        logging.info('path_url:' + path_url)
        # permission_list = session.get('user_permission_list')
        user_id = session.get('user_id')
        permission_list = permission_view.get_user_permission_all_url_list(user_id)
        if path_url in permission_list:
            return True
        else:
            return False


class SysUserHistory(SurrogatePK, Model):
    __tablename__ = 'sys_user_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(64))  # 用户ID
    mobile = Column(String(64))  # 用户手机号
    email = Column(String(64))  # 用户邮箱
    chat_code = Column(String(64))  # 用户微信号
    org_id = Column(String(64))  # 用户的机构 id
    status = Column(String(16))
    create_by = Column(String(64))
    create_time = Column(DateTime)
    update_by = Column(String(64))
    update_time = Column(DateTime)
    start_time = Column(DateTime)  # 工作开始时间
    end_time = Column(DateTime)  # 工作结束时间


class SysUserRole(SurrogatePK, Model):
    __tablename__ = 'sys_user_role'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(64))  # 用户ID
    username = Column(String(64))  # 用户登录名
    role_id = Column(String(64))  # 角色ID
    org_id = Column(String(64))  # 用户的机构 id
    create_by = Column(String(64))
    update_by = Column(String(64))
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class SysDict(SurrogatePK, Model):
    __tablename__ = 'sys_dict'

    id = Column(Integer, primary_key=True)
    dict_name = Column(String(64), server_default=text("''"))  # 名称
    dict_id = Column(String(64), index=True, server_default=text("''"))  # 编码
    dict_type = Column(Integer)  # 字典类型
    description = Column(String(255), server_default=text("''"))  # 类型描述
    sort = Column(String(64), server_default=text("''"))  # 类型排序
    create_by = Column(String(64), server_default=text("''"))  # 创建者
    create_time = Column(DateTime, default=dt.datetime.now)
    update_by = Column(String(64), server_default=text("''"))
    update_time = Column(String(255), default=dt.datetime.now)
    remarks = Column(String(64), server_default=text("''"))
    del_flag = Column(Integer, server_default=text("1"))  # 是否删除（1：是；0：否）

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def to_dict(self):
        table_dict = dict()
        for c in self.__table__.columns:
            if getattr(self, c.name, None):
                table_dict[c.name] = str(getattr(self, c.name, None))
            else:
                table_dict[c.name] = None
        return table_dict

class SysMessage(SurrogatePK, Model):
    __tablename__ = 'sys_message'

    id = Column(Integer, primary_key=True)

    msg_id = Column(String(64))
    msg_type = Column(String(16))  # 消息类型
    msg_title = Column(String(64))  # 消息主题
    msg_content = Column(String)  # 消息内容
    msg_sender = Column(String(64))  # 发送者
    msg_receiver = Column(String(64))  # 接收者
    msg_date = Column(DateTime, default=dt.datetime.now)  # 接收日期
    msg_delete = Column(Integer, server_default=text("'0'"))  # 删除状态
    create_by = Column(String(64))  # 创建者
    update_by = Column(String(64))  # 修改人
    create_time = Column(DateTime, default=dt.datetime.now)  # 创建时间
    update_time = Column(DateTime, default=dt.datetime.now)  # 修改时间


class SysSign(SurrogatePK, Model):
    __tablename__ = 'sys_sign'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(16), nullable=False)  # 用户id
    sign_in_time = Column(DateTime, nullable=False)  # 签到时间
    sign_out_time = Column(DateTime, nullable=False)  # 签出时间
    latitude = Column(String(64), nullable=False)  # 经度
    longitude = Column(String(64), nullable=False)  # 纬度
    create_time = Column(DateTime)
    create_by = Column(String(16))
    update_time = Column(DateTime)
    update_by = Column(String(16))

