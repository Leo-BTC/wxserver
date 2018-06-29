#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/30 下午3:26
# @Author  : czw@rich-f.com
# @Site    : www.rich-f.com
# @File    : assets.py
# @Software: 富融钱通平台
# @Function: 静态资源文件管理


from flask_assets import Bundle, Environment

homecss = Bundle(
    'libs/pc/slide/css/slide.css',
    # 'libs/pc/css/pc-new.css',
    'libs/font-awesome/pc-style.css',
    'libs/font-awesome/font-awesome.min.css',
    'libs/font-awesome/style.css',
    'libs/font-awesome/pe-icon-7-stroke.css',
    filters='cssmin',
    output='public/css/home.css'
)

datetime_js = Bundle(
    'libs/bootstrap/js/moment.min.js',
    'libs/thirdparty/zh-cn.js',
    'libs/jQuery/jquery.sharrre.js',
    'libs/jQuery/demo.js',
    'libs/bootstrap/js/bootstrap-datetimepicker.js',
    filters='jsmin',
    output='public/js/datetimepicker.js'
)

css = Bundle(
    'libs/font-awesome/font-awesome.min.css',
    'libs/font-awesome/style.css',
    'libs/bootstrap/css/bootstrap.min.css',
    'libs/bootstrap/css/light-bootstrap-dashboard.css',
    'libs/bootstrap/css/bootstrap-duallistbox.css',
    'libs/font-awesome/jquery.step.css',
    filters='cssmin',
    output='public/css/common.css'
)
# css = Bundle(
#     'libs/font-awesome/font-awesome.min.css',
#     'libs/font-awesome/style.css',
#     'libs/pc/css/pc-new.css',
#     'libs/bootstrap/css/bootstrap.min.css',
#     'libs/bootstrap/css/light-bootstrap-dashboard.css',
#     filters='cssmin',
#     output='public/css/common.css'
# )



jquery_js = Bundle(
    'libs/jQuery/jquery.min.js',
    'libs/jQuery/jquery-ui.min.js',
    filters='jsmin',
    output='public/js/jquery.js'
)

js = Bundle(
    'libs/dialog/js/sweetalert2.js',
    'libs/bootstrap/js/bootstrap.min.js',
    'libs/bootstrap/js/light-bootstrap-dashboard.js',
    'libs/bootstrap/js/jquery.bootstrap-duallistbox.js',
    'libs/bootstrap/js/jquery.step.min.js',

    filters='jsmin',
    output='public/js/common.js'
)
home_js = Bundle(
    'libs/jQuery/jquery-1.11.2.min.js',
    'libs/jQuery/main-script.min.js',
    filters='jsmin',
    output='public/js/home.js'
)

table_js = Bundle(
    'libs/bootstrap/js/bootstrap-table.js',
    filters='jsmin',
    output='public/js/table.js'
)


select2_js = Bundle(
    'libs/select/js/select2.full.js',
    'libs/select/js/select2.js',
    filters='jsmin',
    output='public/js/select2_js.js'
)

select_css = Bundle(
    'libs/select/css/select2.css',
    filters='cssmin',
    output='public/css/select.css'
)

env = Environment()
env.register('home_css', homecss)
env.register('js_all', js)
env.register('css_all', css)
env.register('table_js', table_js)
env.register('jquery_js', jquery_js)
env.register('home_js', home_js)
env.register('datetime_js',datetime_js)
env.register('select2_js',select2_js)
env.register('select_css', select_css)

