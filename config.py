import os
"""
Flask 的配置文件本身实质是 Python 文件。
只有全部是大写字母的变量才会被配置对象所使用。 因此请确保使用大写字母。
使用时，需要先将配置导入环境变量，比如这样：
export YOURAPPLICATION_SETTINGS=/path/to/settings.cfg
"""

DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = os.urandom(24)
USERNAME = 'admin'
PASSWORD = 'default'