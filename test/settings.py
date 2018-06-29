#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午4:27
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : settings.py
# @Software: 富融钱通
# @Function: 系统配置类
import datetime
import os
from celery.schedules import crontab


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('testWEB_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    WX_OPEN_ID_URL = 'https://api.weixin.qq.com/sns/jscode2session'
    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    # REDIS配置
    # CELERY_IMPORTS = ('richwecsweb.terminal',)  # celery 任务在richwecsweb.ternimal目录下
    # CELERY_ENABLE_UTC = False  # 如果他设置成假，将使用系统本地时区
    # CELERY_CREATE_MISSING_QUEUES = True  # 某个程序中出现的队列，在broker中不存在，则立刻创建它
    # CELERYD_FORCE_EXECV = True      # 非常重要,有些情况下可以防止死锁
    # CELERYD_PREFETCH_MULTIPLIER = 1  # celery worker 每次去rabbitmq取任务的数量，我这里预取了4个慢慢执行,因为任务有长有短没有预取太多
    # CELERYD_CONCURRENCY = 2  # 并发worker数
    # CELERYD_MAX_TASKS_PER_CHILD = 100       # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
    # CELERY_DISABLE_RATE_LIMITS = True  # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
    # CELERY_BROKER_URL = 'amqp://admin:richfadmin@127.0.0.1:5672'  # 绑定的MQ---ip
    #CELERY_EVENT_QUEUE_TTL = 5
    #CELERY_RESULT_BACKEND = 'amqp://admin:richfadmin@127.0.0.1:5672'

    TCP_SERVER_URL = '127.0.0.1'
    # 指定日志的格式，按照每天一个日志文件的方式
    LOG_FILE = './logs/{0}-{1}.log'.format('test', datetime.datetime.now().strftime("%Y-%m-%d"))
    # BAIDU_MAP_URL = "http://api.map.baidu.com/geocoder/v2"
    LOGCONFIG = {
        'version': 1,
        'disable_existing_loggers': False,

        'filters': {
            'require_debug_false': {
                '()': 'test.logging.log.RequestFilter'
            }
        },
        'formatters': {
            'simple': {
                'format': '[%(levelname)s] %(module)s : %(message)s'
            },
            'verbose': {
                'format':
                    '[%(asctime)s] [%(levelname)s] %(module)s : %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',  # TODO
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'file': {
                'level': 'DEBUG',  # TODO
                'class': 'logging.FileHandler',
                'formatter': 'verbose',
                'filename': LOG_FILE,
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['file', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://test:123456@127.0.0.1/test?charset=utf8'  # TODO: Chang
    SQLALCHEMY_POOL_SIZE = 10
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    JSON_AS_ASCII = False



class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://test:123456@127.0.0.1/test?charset=utf8'  # TODO: Chang
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    JSON_AS_ASCII = False


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
