import os
import flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):
    """
    setUp() 方法中会创建一个新的测试客户端并初始化一个新的数据库。
    在每个独立的测试函数运行前都会调用这个方法。
    在设置中 TESTING 标志开启，这意味着在请求时关闭错误捕捉，
    以便于在执行测试请求时得到更好的错误报告。
    """
    def setUp(self):
        # 因为 SQLite3 是基于文件系统的，所以我们可以方便地使用临时文件模块来创建一个临时数据库并初始化它。
        #  mkstemp() 函数返回两个东西：一个低级别的文件句柄和一个随机文件名(即文件句柄和文件名)。
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        """
        tearDown() 方法的功能是在测试结束后关闭文件，
        并在文件系统中删除数据库文件。
        os.close可以关闭一个文件的描述符（句柄）
        """
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        # assert 'No entries here so far' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username = username,
            password = password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert 'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'Invalid password' in rv.data

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data

if __name__ == '__main__':
    unittest.main()