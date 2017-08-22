# coding=utf-8
from pymongo import MongoClient
import pymongo
from passlib.hash import sha256_crypt


# Нужно продумать, что бы в базе изначально была строчка админа, чтобы можно было уже с ней сравниквать
# полученные значения и гоовриьт есть там такое или нет


class Register:
    def __init__(self):
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll = db.coll_reg
            self.user_id = 0

    def new_user(self, username, email, password, tracking):
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
        try:
            get_id = self.coll.find_one({'username' : username})
            return get_id['user_id']
        except Exception as e:
            return str(e)

    def get_tracking(self, username):
        try:
            track = self.coll.find_one({'username': username})
            return track['tracking']
        except Exception as e:
            return str(e)


    def del_user(self, username):
        try:
            self.coll.remove({'username' : username})
            ans = username + 'has been deleted'
            return ans
        except Exception as e:
            return str(e)

    def get_all(self):
        try:
            return self.coll.find({})
        except Exception as e:
            return str(e)

    def del_all(self):
        self.coll.remove(None)
        return 'del all'


class Log_in:
    def __init__(self):
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll = db.coll_reg

    def login_user(self,username):
        tmp = self.coll.find_one({'username': username})
        if tmp is None:
            return 'bad'
        else:
            return 'ok'

    def get_pwd(self,username):
        tmp = self.coll.find_one({'username': username})
        if tmp is None:
            return  'bad'
        else:
            return tmp['password']


