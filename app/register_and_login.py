# coding=utf-8
from pymongo import MongoClient
import pymongo
from passlib.hash import sha256_crypt


class Register(object):
    """This is Registration user class

    This class represents user registration
    Methods:
        addUser
        getIdUser
        getTracking
        getAll
        delUser
        delAll
        """

    def __init__(self):
        """Creating a link to the MongoDB

        :return: Register object.
        """
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll = db.coll_reg
            self.user_id = 0

    def add_user(self, username, email, password, tracking):
        """Use this method to add a user

        This method adds user data to the database
        his nickname, password, e-mail address, and the place where he left the session,
        in the future to track the user

        The user ID is created as it is added to the database. User ID is unique.

        If the user name already exists in the database, the method will display an error message:
        "That username is already taken, please choose another"

        If such an e-mail address is already in the database, the method will display an error message:
        "This email is already in use."

        :param username: Integer or String : Unique username
        :param email: String : Unique email
        :param password: String : md5 password
        :param tracking: String : Path user
        :return: String : ok. if False - > error message
        """
        coll = self.coll
        user_check = coll.find_one({'username': username})
        if user_check is not None:
            check = 'That username is already taken, please choose another'
            return check
        user_check = coll.find_one({'email': email})
        if user_check is not None:
            check = 'This email is already in use.'
            return check
        u_id = coll.find({}).count()
        d = {'user_id': u_id + 1,
             'username': username,
             'email': email,
             'password': password,
             'tracking': tracking
             }
        coll.insert(d)
        self.user_id = u_id + 1
        check = 'ok'
        return check

    def get_id_user(self, username):
        """Use this method to get the user ID

        If this user does not exist, the method will display an error message
        "This user does not exist"

        :param username: String : Unique username
        :return: Integer : user ID. If false - >  error message
        """
        try:
            get_id = self.coll.find_one({'username': username})
            return get_id['user_id']
        except Exception:
            return 'This user does not exist'

    def get_tracking(self, username):
        """Use this method to track user sessions

        If this user does not exist, the method will display an error message
        "This user does not exist"

        :param username: String : Unique username
        :return: String : track. If false - >  error message
        """
        try:
            track = self.coll.find_one({'username': username})
            return track['tracking']
        except Exception as e:
            return str(e)

    def get_all(self):
        """Use this method to get all user information

        :return: MongoDb object. If false - > error message
        """
        try:
            return self.coll.find({})
        except Exception as e:
            return str(e)

    def del_user(self, username):
        """

        :param username:
        :return:
        """
        try:
            self.coll.remove({'username': username})
            ans = username + 'has been deleted'
            return ans
        except Exception as e:
            return str(e)

    def del_all(self):
        """

        :return:
        """
        self.coll.remove(None)
        return 'del all'


a = Register()
# a.del_all()
tmp = a.get_all()
for t in tmp:
    print t


class LogIn(object):
    """
    Данный класс реализует проверку пользователя при авторизации. сравнивает его логин и пароль.
    Все пароли закодированы с помощью sha-256 и хранятся в БД. через html пользователь может сварерить свой
    ввод пароля с тем паролем, котрый хранится в БД
    """

    def __init__(self):
        """

        """
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll = db.coll_reg

    def login_user(self, username):
        """

        :param username:
        :return:
        """
        tmp = self.coll.find_one({'username': username})
        if tmp is None:
            return 'bad'
        else:
            return 'ok'

    def get_user_id(self, username):
        """

        :param username:
        :return:
        """
        try:
            tmp = self.coll.find_one({'username': username})
            return tmp['user_id']
        except Exception:
            return 'This user does not exist'

    def get_pwd(self, username):
        """Use this method to retrieve a user password

        If this user does not exist then the method will write an error message
        "bad"

        :param username: String or Integer : Unique username
        :return: String : password user or error message
        """
        tmp = self.coll.find_one({'username': username})
        if tmp is None:
            return 'bad'
        else:
            return tmp['password']

    def change_password(self, username, user_id, password):
        """

        :param username:
        :param user_id:
        :param password:
        :return:
        """
        try:
            self.coll.update({'username': username,
                              'user_id': user_id},
                             {'$set': {'password': password}})
        except Exception:
            return 'Something is wrong'

    def del_user(self, username, user_id):
        """

        :param username:
        :param user_id:
        :return:
        """
        try:
            self.coll.delete_one(({'username': username,
                                   'user_id': user_id}))
        except Exception:
            return 'This user does not exist'

    def change_email(self, username, user_id, new_email):
        """

        :param username:
        :param user_id:
        :param new_email:
        :return:
        """
        try:
            self.coll.update({'username': username,
                              'user_id': user_id},
                             {'$set': {'email': new_email}})
        except Exception:
            return 'Something is wrong'
