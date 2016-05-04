# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application
app = Flask(__name__)

"""
from_object() 会查看给定的对象（如果该对象是一个字符串就会直接导入它），
搜索对象中所有变量名均为大字字母的变量。在我们的应用中，已经将配置写在前面了。
你可以把这些配置放到一个独立的文件中。
"""
app.config.from_object(__name__)


def connect_db():
    """
    我们还添加了一个方便连接指定数据库的方法。
    这个方法可以用于在请求时打开连接，也可以用于 Python 交互终端或代码中。以后会派上用场。
    """
    return sqlite3.connect(app.config['DATABASE'])


if __name__ == '__main__':
    app.run()