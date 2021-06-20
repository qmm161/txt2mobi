# coding=utf8

import os
import sys
import requests
import configparser
import socket
import http.server
import socketserver
from txt2mobi.exceptions import KindleGenNotInstalledError



def current_working_dir():
    return os.getcwd()


def init_project():
    book_name = ''
    dir_path = current_working_dir()
    onlyfiles = [f for f in os.listdir(dir_path) if f.endswith('txt')]
    for file_name in onlyfiles:
        book_name = file_name.split('.')[0]
    rows = []
    rows.append('[txt2mobi]')
    rows.append('kindlegen=kindlegen')
    rows.append('')
    rows.append('[book]')
    rows.append('cover-img=cover.jpg')
    rows.append('title=%s' % book_name)
    rows.append('author=作者')
    rows.append('max-chapter=1500')
    with open(os.path.join(current_working_dir(), '.project.ini'), 'w') as f:
        f.write("\n".join(rows))
        f.close()


def check_kindlgen(command='kindlegen'):
    rt = os.system(command)
    if rt:
        raise KindleGenNotInstalledError()

class ProjectConfig(object):
    def __init__(self):
        try:
            file_path = os.path.join(current_working_dir(), '.project.ini')
            self.cf = configparser.ConfigParser()
            self.cf.read(file_path)
        except Exception:
            print ("当前目录未初始化")
            sys.exit(1)


    @property
    def gen_command(self):
        return self.cf.get('txt2mobi', 'kindlegen')

    @property
    def cover_image(self):
        return self.cf.get('book', 'cover-img')

    @property
    def title(self):
        return self.cf.get('book', 'title')

    @property
    def author(self):
        return self.cf.get('book', 'author')

    @property
    def max_chapter(self):
        try:
            return self.cf.getint('book', 'max-chapter')
        except:
            return 1500


def codeTrans(code):
    """
    将chardet返回的coding名字转换成系统用的
    :param code:
    :type code:
    :return:
    :rtype:
    """
    codings = {
        'utf-8': 'utf-8',
        'GB2312': 'GBK'
    }
    return codings.get(code, 'utf-8')


def no_html(input_str):
    import re
    return re.sub(r'</?\w+[^>]*>', '', input_str)


def getIp():
    """
    获取本机IP地址
    :return:
    :rtype:
    """
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr


def start_server():
    """
    开启一个HTTP服务器用于Kindle下载生成的.mobi文件
    :return:
    :rtype:
    """
    PORT = 8000
    Handler = http.server.SimpleHTTPServer
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print ("打开Kindle:体验版网页浏览器, 输入http://%s:8000 点击project.mobi下载" % getIp())
    httpd.serve_forever()

