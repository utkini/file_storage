from pymongo import MongoClient
import pymongo
from passlib.hash import sha256_crypt


def connection():
    with MongoClient('localhost', 27017) as mongo:
        db = mongo.db_storage
        coll = db.ip_coll
        coll.remove(None)
        count = 0
        while count < 5:
            user = raw_input('insert username please ')
            pwd = raw_input('insert password please ')
            cr_pwd = sha256_crypt.encrypt(pwd)
            user_check = coll.find_one({'username': user})
            if user_check is not None:
                print 'this user is already exist'
            else:
                d = {'username': user, 'password': cr_pwd}
                coll.insert(d)
                count = coll.find({}).count()
        if coll.find().count() == 2:
            for col in coll.find({}):
                print col['username']



connection()
