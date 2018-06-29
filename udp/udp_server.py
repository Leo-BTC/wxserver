# Copyright (c) 2012 Denis Bilenko. See LICENSE for details.
"""A simple UDP server.

For every message received, it sends a reply back.

You can use udp_client.py to send a message.
"""

from gevent.server import DatagramServer
import logging
import requests

BASE_URL = 'http://127.0.0.1:8000/'
SECRET = '430f787612274bc09668d515bfcb1176'

logger = logging.getLogger('udp-server')
LEVEL = logging.DEBUG
logger.setLevel(LEVEL)

ch = logging.StreamHandler()
ch.setLevel(LEVEL)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

port = ':10006'  # 端口号


class EchoServer(DatagramServer):
    def handle(self, data, address):
        """
        :param data: 请求数据
        :param address:udp 请求地址
        :return:
        """
        try:

            logger.debug('%s: got %r' % (address[0], bytes_encode(data)))
            data = bytes_encode(data)
            post_url = BASE_URL + 'real_time/terminal.push'

            response_data = requests.post(url=post_url, json=eval(data), headers={'content-type': 'application/json'})
            logger.debug("response data = %s", response_data)
            self.sendto(str({'code': '00'}).encode('utf-8'), address)

        except IOError as e:
            logger.exception(e)


def bytes_encode(b, charset='utf-8'):
    """
    字节转为字符串
    :param b:
    :param charset:
    :return:
    """
    return str(b, charset)


if __name__ == '__main__':
    logger.info('receiving data grams on %s' % port)
    EchoServer(port).serve_forever()
