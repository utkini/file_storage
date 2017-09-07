import unittest

from app.usersdata import UsersData


class TestLUsersData(unittest.TestCase):
    def setUp(self):
        self.a = UsersData()

    def tearDown(self):
        del self.a

    def test_1_acreate_dir_for_user(self):
        # True
        self.a.del_all()
        self.assertIsNone(self.a.create_dir_for_user('admin', 2))
        self.assertIsNone(self.a.create_dir_for_user('1224', 1))

    def test_2_add_file(self):
        # isinstance
        self.assertIsInstance(self.a.add_file('admin', 2, 'words.txt', 'admin'), dict)
        self.assertIsInstance(self.a.add_file('admin', 2, 'words.txt', 'admin'), dict)
        self.assertIsInstance(self.a.add_file('1224', 1, 'mail.pdf', '1224'), dict)
        self.assertIsInstance(self.a.add_file('1224', 1, 'song.mp3', '1224'), dict)

        self.assertEqual(self.a.add_file('admin', 2, 'words.txte', 'admin'),
                         'The extension of these files are not supported by this system.')
        self.assertEqual(self.a.add_file('1224', 1, 'scrypt.py', '1224'),
                         'The extension of these files are not supported by this system.')
        self.assertEqual(self.a.add_file('1224', 1, '', '1224'),
                         'The extension of these files are not supported by this system.')

    def test_3_rename_file(self):
        self.assertIsNone(self.a.rename_file('admin', 2, 'admin', 'words.txt', 'file.txt'))
        self.assertIsNone(self.a.rename_file('admin', 2, 'admin', 'words(1).txt', 'file.txt'))






if __name__ == "__main__":
    unittest.main()
