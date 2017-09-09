# coding=utf-8
import unittest

from app.api.register_and_login import LogIn


class TestLogIn(unittest.TestCase):
    def setUp(self):
        self.a = LogIn()

    def tearDown(self):
        del self.a

    def test_login_user(self):
        self.assertEqual(self.a.login_user('2'), 'bad')
        self.assertEqual(self.a.login_user('admin'), 'ok')
        self.assertEqual(self.a.login_user('eva'), 'bad')
        self.assertEqual(self.a.login_user(''), 'bad')

    def test_get_user_id(self):
        self.assertIsInstance(self.a.get_user_id('2'), str)
        self.assertIsInstance(self.a.get_user_id('admin'), int)
        self.assertIsInstance(self.a.get_user_id(''), str)

    def test_get_pwd(self):
        self.assertIs(self.a.get_pwd(''), 'bad')
        self.assertIs(self.a.get_pwd('eva'), 'bad')
        self.assertIsInstance(self.a.get_pwd('admin'), unicode)

    def test_change_password(self):
        pass  # нужен md5 для этого

    def test_del_user(self):
        self.assertIs(self.a.del_user('eva', 517), None)
        self.assertIs(self.a.del_user('', 517), None)

    def test_change_email(self):

        # True
        self.assertIs(self.a.change_email('admin', 1, 'guru@mail.ru'), None)
        self.assertIs(self.a.change_email('', 1, 'grub@mail.ru'), None)
        self.assertIs(self.a.change_email('admin', 1, 'admin@admin.ru'), None)
        # False
        self.assertIsInstance(self.a.change_email('eva', 517, 'gore@ml'), str)
        self.assertIsInstance(self.a.change_email('admin', 517, 'gara@mailru'), str)


if __name__ == "__main__":
    unittest.main()
