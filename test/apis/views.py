from flask import jsonify,Blueprint,request
import logging,requests
from test.responsecode import ResponseCode
from test.settings import Config
from test.extensions import csrf_protect
from test.apis import api
import requests

blueprint = Blueprint('weixin', __name__, url_prefix='/wx', static_folder='../static')


@csrf_protect.exempt
@blueprint.route('/login',methods=['POST'])
def login():
    """
    微信小程序登陆获取open_id
    :return:
    """
    logging.info("login")
    try:
        data = eval(request.data.decode())
        code = data['code']
        app_id = data['app_id']
        secret = data['secret']
        params = {
            'appid': app_id,
            'secret': secret,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.get(url=Config.WX_OPEN_ID_URL, params=params)  # 向微信请求获取open_id
        open_id = eval(response.text)['openid']
        return jsonify({'data': open_id})
    except Exception as e:
        logging.debug(e)
        return jsonify({'code':ResponseCode.PARAMETER_ERROR,'msg':'系统内部异常，请联系管理员'})


@csrf_protect.exempt
@blueprint.route('/check', methods=['POST'])
def check():
    """
    根据获取的openid查询数据库，如果存在则进入货币列表页，否则需要填写手机号码注册
    :return:
    """
    logging.info("check")
    try:
        param = request.get_json()
        open_id =param.get('open_id')  # 获取open_id
        res = api.check_open_id(open_id=open_id)
        return jsonify(res)
    except Exception as e:
        logging.debug(e)
        return jsonify({'code':ResponseCode.ERROR,'msg':'系统内部异常，请联系管理员'})


@csrf_protect.exempt
@blueprint.route('/register', methods=['POST'])
def register():
    """
    注册
    :return:
    """
    logging.info("register")
    try:
        param = request.get_json()
        open_id = param.get('open_id')
        uid = param.get('uid')
        address = param.get('address')
        avatar = param.get('avater')
        username =param.get('username')
        res = api.wx_register(username=username,uid=uid,open_id=open_id,avatar=avatar,address=address)
        return jsonify(res)
    except Exception as e:
        logging.debug(e)
        return jsonify({'code':ResponseCode.PARAMETER_ERROR})
@csrf_protect.exempt
@blueprint.route('/list', methods=['POST'])
def list():
    """
    根据获取的openid查询数据库，如果存在则进入货币列表页，否则需要填写手机号码注册
    :return:
    """
    logging.info("list")
    try:
        param = request.get_json()
        open_id =param.get('open_id')  # 获取open_id
        res = api.price(open_id=open_id)
        return jsonify(res)
    except Exception as e:
        logging.debug(e)
        return jsonify({'code':ResponseCode.ERROR,'msg':'系统内部异常，请联系管理员'})
#加入组合
@csrf_protect.exempt
@blueprint.route('/jointoken', methods=['POST'])
def jointoken():
    logging.info('jointoken')
    try:
        param = request.get_json()
        tokenname = param.get('name')
        dui = param.get('dui')
        open_id = param.get('open_id')
        res = api.jointoken(tokenname=tokenname,open_id=open_id,dui=dui)
        return jsonify(res)
    except Exception as e:
        logging.debug(e)
        return jsonify({'code': ResponseCode.ERROR, 'msg': '加入失败，请联系管理员'})
#加载用户所有加入的组合
@csrf_protect.exempt
@blueprint.route('/alltoken', methods=['POST'])
def alltoken():
    logging.info('alltokenviews')
    try:
        param = request.get_json()
        open_id = param.get('open_id')  # 获取open_id
        res = api.alltoken(open_id=open_id)
        return jsonify(res)
    except Exception as e:
        logging.info(e)
        return jsonify({'code': ResponseCode.ERROR, 'msg': '获取组合失败，请联系管理员'})
@csrf_protect.exempt
@blueprint.route('/gate', methods=['GET','POST'])
def gate():
    try:
        url='https://data.gateio.io/api2/1/ticker/usdt_cny'
        data= requests.get(url=url)
        data = data.json()
        res =data['last']
        return res
    except Exception as e:
        logging.info(e)
        return jsonify({'code': ResponseCode.ERROR, 'msg': '获取，USDT_CNY失败，请联系管理员'})

#删除用户组合
@csrf_protect.exempt
@blueprint.route('/deletetoken', methods=['GET','POST'])
def deletetoken():
    try:
        logging.info('deletetoken')
        try:
            param = request.get_json()
            tokenname = param.get('name')
            tokenname = tokenname['name']
            open_id = param.get('open_id')
            length = param.get('length')
            res = api.deletetoken(tokenname=tokenname,open_id=open_id,length=length)
            return jsonify(res)
        except Exception as e:
            logging.debug(e)
            return jsonify({'code': ResponseCode.ERROR, 'msg': '加入失败，请联系管理员'})
    except Exception as e:
        logging.info(e)
        return jsonify({'code': ResponseCode.ERROR, 'msg': '删除错误，请联系管理员'})
#获取用户资料
@csrf_protect.exempt
@blueprint.route('/userinfo', methods=['POST'])
def userinfo():
    logging.info("deletetoken")
    try:
        param = request.get_json()
        open_id = param.get('open_id')  # 获取open_id
        res = api.userinfo(open_id=open_id)
        return jsonify(res)
    except Exception as e:
        logging.debug(e)
        return jsonify({'code': ResponseCode.ERROR, 'msg': '系统内部异常，请联系管理员'})
#更新token的百分比和数量
@csrf_protect.exempt
@blueprint.route('/edittoken', methods=['GET','POST'])
def edittoken():
    logging.info("edittoken")
    try:
        param = request.get_json()
        open_id = param.get('open_id')
        numbers = param.get('numbers')
        zhanbi = param.get('moren')
        tokenname = param.get('tokenname')
        dui = param.get('dui')
        res = api.edittoken(open_id=open_id,numbers=numbers,zhanbi=zhanbi,tokenname=tokenname,dui=dui)
        return jsonify(res)
    except Exception as e:
        logging.info(e)
        return jsonify({'code': ResponseCode.ERROR, 'msg': '获取，USDT_CNY失败，请联系管理员'})
#更新现金和总金额
@csrf_protect.exempt
@blueprint.route('/editcash', methods=['GET','POST'])
def editcash():
    logging.info("editcash。。。")
    try:
        param = request.get_json()
        print(param)
        open_id = param.get('open_id')
        cash = param.get('cash')
        price = param.get('price')
        length = param.get('length')
        print(length)
        res = api.editcash(open_id=open_id,cash=cash,price=price,length=length)
        return jsonify(res)
    except Exception as e:
        logging.info(e)
        return {'code': ResponseCode.ERROR, 'msg': '修改现金失败，请联系管理员'}