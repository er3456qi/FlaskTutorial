# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash
from contextlib import closing

# configuration 这里移到外部文件config.py里面去了
# DATABASE = '/tmp/flaskr.db'
# DEBUG = True
# SECRET_KEY = 'development key'
# USERNAME = 'admin'
# PASSWORD = 'default'

# create our little application
app = Flask(__name__)

"""
from_object() 会查看给定的对象（如果该对象是一个字符串就会直接导入它），
搜索对象中所有变量名均为大字字母的变量。在我们的应用中，已经将配置写在前面了。
你可以把这些配置放到一个独立的文件中（这里就放到config.py里面去了）。
"""
# app.config.from_object(__name__)


"""
通常，从一个配置文件中导入配置是比较好的做法，
我们使用 from_envvar() 来完成这个工作，把上面的 from_object() 一行替换为下面这行。
这样做就可以设置一个 FLASKR_SETTINGS 的环境变量来指定一个配置文件，并根据该文件来重载缺省的配置。
silent 开关的作用是告诉 Flask 如果没有这个环境变量不要报错。
"""
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """
    我们还添加了一个方便连接指定数据库的方法。
    这个方法可以用于在请求时打开连接，也可以用于 Python 交互终端或代码中。以后会派上用场。
    """
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """
    init_db()的作用是简化创建及初始化数据库的过程。
    closing() 函数允许我们在with代码块内保持数据库连接为打开状态。
    应用对象的 open_resource() 也支持这个功能，可以在with代码块中直接使用。
    open_resource 打开一个位于来源位置（你的flaskr文件夹）的文件并允许你读取文件的内容。
    这里我们把内容读取后直接执行了。
    """
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read)
        db.commit()


@app.before_request
def before_request():
    """
    使用 before_request 装饰器的函数会在请求之前调用，且不传递参数。
    我们把数据库连接保存在 Flask 提供的特殊的 g 对象中。
    这个对象与 每一个请求是一一对应的，并且只在函数内部有效。
    不要在其它对象中储存类似信息， 因为在多线程环境下无效。
    这个特殊的 g 对象会在后台神奇的工作，保证系统正常运行。
    """
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """
    使用 after_request 装饰器的函数会在请求之后调用，且传递发给客户端的响应对象。
    它们必须传递响应对象，所以在出错的情况下就不会执行。因此我们就要用到teardown_request装饰器。
    这个装饰器下的函数在响应对象构建后被调用。它们不允许修改请求，并且他们的返回值被忽略。
    如果请求过程中出错，那么这个错误会传递给每个函数，否则传递None。
    """
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_entries():
    # 这个视图显示所有数据库中的条目。
    # 从指针返回的记录集是一个包含 select 语句查询结果的元组。这里最后给转换成一个字典
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    # 在本视图中检查了用户是否已经登录
    # (即检查会话中是否有 logged_in 键，且对应的值是否为 True ）。
    if not session.get('logged_in'):
        abort(401)
    # 确保在构建 SQL 语句时使用问号而不是使用字符串连接,这样能避免遭受SQL注入攻击。
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash("New entry was successfully posted")
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    登录视图根据配置中的用户名和密码验证用户并在会话中设置 logged_in 键值。
    如果用户通过验证，键值设为 True ，那么用户会被重定向到 show_entries 页面。
    另外闪现一个信息，告诉用户已登录成功。
    如果出现错误，模板会提示错误信息，并让用户重新登录:
    """
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """
    登出视图则正好相反，把键值从会话中删除。
    在这里我们使用了一个小技巧：如果你使用字典的 pop() 方法并且传递了第二个参数（键的缺省值），
    那么当字典中有这个键时就会删除这个键，否则什么也不做。
    这样做的好处是我们不用检查用户是否已经登录了。
    :return:
    """
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()