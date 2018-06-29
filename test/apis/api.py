import logging
from test.responsecode import ResponseCode
import sqlalchemy
from test.apis.models import UserInfo,TokenItem
from sqlalchemy import distinct
def check_open_id(open_id):
    """
    根据open_id查询数据库
    :param open_id: open_id
    :return:
    """
    logging.info("check_open_id")
    try:
        user_obj = UserInfo.query.filter(UserInfo.open_id == open_id).first()
        if user_obj:
            return {'code':ResponseCode.SUCCESS,'data':{'username':user_obj.username,'uid':user_obj.uid,'avatar':user_obj.avatar,'address':user_obj.address},'msg':'查询成功!'}
        else:
            return {'code':ResponseCode.ERROR,'msg':'用户不存在，需要注册'}
    except Exception as e:
        logging.debug(e)
        return {'code':ResponseCode.PARAMETER_ERROR,'msg':''}


def wx_register(username,uid,address,open_id,avatar):
    """
    注册，插入数据库
    :param username:用户名
    :param phone: 手机号
    :param open_id: open_id
    :param avatar: 头像
    :return:
    """
    logging.info("wx_register")
    try:
        UserInfo.create(
            username=username,
            uid=uid,
            address=address,
            open_id=open_id,
            avatar=avatar,
            price=int(1000000),
            number = int(0),
            paihang = '--'
        )
        return {'code':ResponseCode.SUCCESS,'msg':'注册成功'}
    except Exception as e:
        logging.debug(e)
        raise e
#获取虚拟资产信息
def price(open_id):
    logging.info('paice')
    try:
        user_obj = UserInfo.query.filter(UserInfo.open_id == open_id).first()
        token_obj = TokenItem.query.order_by(TokenItem.id.desc()).distinct(TokenItem.tokenname).filter(
            TokenItem.open_id == open_id).all()
        length = len(token_obj)
        if user_obj:
            return {'code': ResponseCode.SUCCESS,
                    'data': {'price': user_obj.price, 'number': user_obj.number, 'paihang': user_obj.paihang,'cash':user_obj.cash},
                    'msg': '查询成功!'}
        else:
            return {'code': ResponseCode.ERROR, 'msg': '用户不存在，需要注册'}
    except Exception as e:
        logging.debug(e)
        raise e
#获取token初始值
def jointoken(tokenname,open_id,dui):
    logging.info('jointoken')
    try:
        TokenItem.create(
            open_id=open_id,
            tokenname = tokenname,
            dui = dui,
            numbers = int(0),
            zhanbi = int(0),
        )
        return {'code': ResponseCode.SUCCESS, 'msg': '加入组合成功'}
    except Exception as e:
        logging.debug(e)
        raise e
#所有token组合
def alltoken(open_id):
    logging.info('alltoken')
    try:
        token_obj = TokenItem.query.order_by(TokenItem.id.desc()).distinct(TokenItem.tokenname).filter(TokenItem.open_id == open_id).all()
        length = len(token_obj)
        if token_obj:
            data = []
            name = []
            length = len(token_obj)
            for i in token_obj:
                if i.tokenname in name:
                    continue
                else:
                    data.append({'tokenname': i.tokenname, 'numbers': i.numbers, 'zhanbi': i.zhanbi,'dui':i.dui})
                    name.append(i.tokenname)
            print(data)
            return {'code': ResponseCode.SUCCESS,
                    'data': data,
                     'length':length,
                    'msg': '查询成功!'}
        else:
            return {'code': ResponseCode.ERROR, 'msg': 'token不存在，需要加入组合'}
    except Exception as e:
        logging.debug(e)
        raise e
def deletetoken(tokenname,open_id):
    token = TokenItem.query.filter_by(tokenname=tokenname,open_id=open_id).all()
    if token:
        TokenItem.delete(
            token
        )
        res = {'code': ResponseCode.SUCCESS, 'msg': '删除成功'}
        return res
    else:
        return {'code': ResponseCode.ERROR, 'msg': 'token不存在，需要加入组合'}
def userinfo(open_id):
    try:
        user_obj = UserInfo.query.filter(UserInfo.open_id == open_id).first()
        if user_obj:
            return {'code': ResponseCode.SUCCESS,
                    'data': {'uid': user_obj.uid, 'address': user_obj.address},
                    'msg': '查询成功!'}
        else:
            return {'code': ResponseCode.ERROR, 'msg': '用户不存在，需要注册'}
    except Exception as e:
        logging.debug(e)
        raise e
def edittoken(open_id,numbers,zhanbi,tokenname,dui):
    try:
        TokenItem.create(
            open_id=open_id,
            numbers=numbers,
            zhanbi = zhanbi,
            tokenname=tokenname,
            dui = dui

                         )
        res = TokenItem.query.order_by(TokenItem.id.desc()).filter_by(open_id=open_id).all()
        length = len(res)
        if res:
            data = []
            name = []
            length = len(res)
            for i in res:
                if i.tokenname in name:
                    continue
                else:
                    data.append({'tokenname': i.tokenname, 'numbers': i.numbers, 'zhanbi': i.zhanbi, 'dui': i.dui})
                    name.append(i.tokenname)
            return {'code': ResponseCode.SUCCESS,
                    'data': data,
                    'length': length,
                    'msg': '查询成功!'}
    except Exception as e:
        logging.info(e)
        raise e
def editcash( open_id,cash,price,length):
    logging.info('editcash')
    print(price)
    try:
        res = UserInfo.query.filter(UserInfo.open_id == open_id,).first()
        UserInfo.update(res,
                        cash = cash,
                        price=price,
                        number=length
                        )
        return {'code': ResponseCode.SUCCESS,
                    'msg': '修改现金成功!'}
    except Exception as e:
        return {'code': ResponseCode.ERROR, 'msg': '修改现金失败，请联系管理员'}