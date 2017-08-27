# coding=utf-8
import hashlib
import os
from pymongo import MongoClient
import pymongo


class UsersData:
    directory = os.getcwd()
    directory = directory + '/users'
    TEXT = {'txt', 'doc', 'docx', 'docm', 'dotm', 'dotx', 'pdf',
            'xls', 'xlsx', 'xlsm', 'xltx', 'xlt', 'xltm', 'pptx',
            'ppt', 'ppsx', 'pps', 'potx', 'pot', 'ppa', 'ppam'}
    PIC = {'jpg', 'jpeg', 'tif', 'tiff', 'png', 'gif', 'bmp'}
    SONG = {'wav', 'mp3', 'wma', 'ogg', 'aac', 'flac'}

    def __init__(self):
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll_d = db.coll_data

    # Данный метод добавляет по username и user_id файл с 3мя параметрами, имя файла, его путь в системе и его путь
    # в вебе.
    def add_data(self, username, user_id, filename, sys_dir, user_dir):
        index = filename.rfind('.')
        format_file = filename[index + 1:]
        fil = {}
        if format_file in self.TEXT or format_file in self.PIC or format_file in self.SONG:
            fil = {'filename': filename,
                   'user_dir': user_dir,
                   'sys_dir': sys_dir}
            self.coll_d.insert({
                'user_data':
                    {
                        'username': username,
                        'user_id': user_id
                    },
                'file': fil,
                'pathways': []
            })
            return 'file added!'
        else:
            return 'somethings wrong'

    # Берем всех и выводим их
    def get_all(self):
        all_d = self.coll_d.find()
        for d in all_d:
            print d

    # Поиск файла по директории, проверяя тот ли это пользователь с помощью двух идентифкаторов username и user_id
    def find_files_in_dirs(self, username, user_id, user_dir):
        files = []
        tmp = self.coll_d.find({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': user_dir})
        for i in tmp:
            files.append(i['file']['filename'])
        return files

    def make_way(self, username, user_id, pathway):
        tmp = self.coll_d.find({'user_data.username': username, 'user_data.user_id': user_id})
        ways = []
        for st in tmp:
            if st['pathways']:
                ways = st['pathways']
        s = set(ways)
        s.add(pathway)
        ways = list(s)
        self.coll_d.update({'user_data.username': username, 'user_data.user_id': user_id},
                           {'$set': {'pathways': ways}})

    def get_ways(self, username, user_id):
        tmp = self.coll_d.find({'user_data.username': username, 'user_data.user_id': user_id})
        for st in tmp:
            if st['pathways']:
                return st['pathways']

        return 'this user has no path'

    # Смена имени директории. Для смены имени нужны все директории в который есть эта директория и их замена этого
    # имени на новое име созданное пользователем.
    def change_dir_name(self, username, user_id, old_user_dir, new_dir_name):
        reg = '^' + old_user_dir
        c = []
        old_way = old_user_dir.rpartition('/')
        sample = self.coll_d.find({'user_data.username': username,
                                   'user_data.user_id': user_id,
                                   'file.user_dir': {'$regex': reg}})
        for sm in sample:
            tmp = sm['file']['user_dir']
            tmp = tmp.replace(old_way[len(old_way)-1],new_dir_name)
            c.append(tmp)
        for i in c:
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': {'$regex':reg}},
                               {'$set': {
                                   'file.user_dir': i
                               }
                               })

    def delete_ways(self, username, user_id, name_dir):
        tmp = self.coll_d.find({'user_data.username': username, 'user_data.user_id': user_id})
        new_ways = []
        ways = []
        for st in tmp:
            if st['pathways']:
                ways = st['pathways']
        for way in ways:
            if way != name_dir:
                new_ways.append(way)
        self.coll_d.update({'user_data.username': username, 'user_data.user_id': user_id},
                           {'$set':
                                {'pathways': new_ways}
                            })

    # Создание директории по пути файла для дальнейшено его там расположения
    def create_dir_for_file(self, filename):
        m = hashlib.md5()
        m.update(filename)
        new_dir = self.directory + '/' + m.hexdigest()[0:2]
        try:
            os.mkdir(new_dir)
            new_dir = new_dir + '/' + m.hexdigest()[2:4]
            os.mkdir(new_dir)
        except OSError:
            try:
                new_dir = new_dir + '/' + m.hexdigest()[2:4]
                os.mkdir(new_dir)
            except Exception:
                pass
        return new_dir

    def del_all(self):
        self.coll_d.remove(None)
        return 'del all'


b = UsersData()
b.del_all()

b.add_data('adam', 234, 'users.txt', '/users/a', '/new/ma/ran')
b.add_data('adam', 234, 'main.txt', '/users/b', '/new/ma')
b.add_data('adam', 234, 'users.pdf', '/users/a', '/new')
b.add_data('adam', 234, 'users.mp3', '/users/a/b', '/new/song')
b.add_data('adam', 234, 'users.jpg', '/users/a', '/new/pic')
b.add_data('eva', 122, 'text.pdf', '/users/l2', '/my/gen')

b.make_way('adam', 234, '/new')
b.make_way('adam', 234, '/new/ma')
b.make_way('adam', 234, '/new/song')
b.make_way('adam', 234, '/new/pic')

print b.get_ways('adam', 234)
b.delete_ways('adam', 234, '/new/pic')
b.change_dir_name('adam', 234, '/new/n', 'now')
b.get_all()
