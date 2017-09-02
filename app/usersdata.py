# coding=utf-8
import hashlib
import os
import shutil
from collections import OrderedDict

from pymongo import MongoClient
import pymongo


class UsersData:
    """ Данныйкласс предназначен для основных действи пользователя:
    добавление файла, создание директории, получение путей этих директорий,
    изменений имен файлов и директорий, получение файлов в директории, удаление директорий,
    удаление файлов, обновление файлов. просмотр всех значений в БД удаление всех значений из БД.
    """
    directory = '/home/ihgorek/Documents/file_storage/app/users'
    TEXT = {'txt', 'doc', 'docx', 'docm', 'dotm', 'dotx', 'pdf',
            'xls', 'xlsx', 'xlsm', 'xltx', 'xlt', 'xltm', 'pptx',
            'ppt', 'ppsx', 'pps', 'potx', 'pot', 'ppa', 'ppam'}
    PIC = {'jpg', 'jpeg', 'tif', 'tiff', 'png', 'gif', 'bmp'}
    SONG = {'wav', 'mp3', 'wma', 'ogg', 'aac', 'flac'}

    def __init__(self):
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll_d = db.coll_data

    '''
    Данный метод испульзуется при создании нового пользователя.
    он создает его корневую папку в списке pathways для дальнейшей работы.
    '''
    def create_dir_for_user(self, username, user_id):
        user_dir = '/' + username
        user_dir_os = self.directory + user_dir
        try:
            self.coll_d.insert({'user_data':
                {
                    'username': username,
                    'user_id': user_id
                },
                'file': {},
                'pathways': [user_dir]})
            os.mkdir(user_dir_os)
        except Exception as e:
            print str(e)

    '''
    Данный метод реализует добавление файла в БД и создание директорий на сервере и директорий для пользователя
    для хранения этого файла.
    На сервере файл сохраняется в папках созданных с помощью алгоритма md5.
    '''
    def add_file(self, username, user_id, filename, user_dir=''):
        name_file = filename.rpartition('.')[0]
        new_user_dir = '/' + user_dir
        sample = self.coll_d.find({'user_data.username': username,
                                   'user_data.user_id': user_id,
                                   'file.user_dir': new_user_dir,
                                   'file.filename': {'$regex': name_file}
                                   }).count()
        if sample != 0:
            sep_filename = filename.rpartition('.')
            new_filename = sep_filename[0] + '(' + str(sample) + ')'
            new_filename = new_filename + '.' + sep_filename[-1]
        else:
            new_filename = filename
        file_dir = user_dir + '/' + new_filename
        m = hashlib.md5()
        m.update(file_dir)
        file_dir = self.directory + '/' + username + '/' + m.hexdigest()[0:2]
        new_dir = '/' + username + '/' + m.hexdigest()[0:2]
        try:
            os.mkdir(file_dir)
            file_dir = file_dir + '/' + m.hexdigest()[2:4]
            new_dir = new_dir + '/' + m.hexdigest()[2:4]
            os.mkdir(file_dir)
        except OSError:
            try:
                file_dir = file_dir + '/' + m.hexdigest()[2:4]
                new_dir = new_dir + '/' + m.hexdigest()[2:4]
                os.mkdir(file_dir)
            except Exception as e:
                print str(e)
        sys_dir = new_dir
        tmp = new_filename.rpartition('.')
        format_file = tmp[-1]

        # count = self.coll_d.find({'user_data.username': username,
        #                           'user_data.user_id': user_id,
        #                           'file.user_dir': new_user_dir,
        #                           'file.filename':filename}).count()
        # if count == 1:
        #     return 'This file exist'
        if format_file in self.TEXT or format_file in self.PIC or format_file in self.SONG:
            fil = {'filename': new_filename,
                   'user_dir': new_user_dir,
                   'sys_dir': sys_dir}
            self.coll_d.insert({
                'user_data':
                    {
                        'username': username,
                        'user_id': user_id
                    },
                'file': fil
            })
            cur = self.coll_d.find_one({'user_data.username': username,
                                        'user_data.user_id': user_id,
                                        'file':{}})
            s = cur['pathways']
            s = set(s)
            s.add(new_user_dir)
            s = list(s)
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file': {} },
                                {'$set': {'pathways': s}})
            d = {}
            d['file_dir']=file_dir
            d['filename'] = new_filename
            return d
        else:
            return 'The extension of these files are not supported by this system.'

    def del_file(self, username, user_id, filename, user_dir):
        user_dir = '/' + user_dir
        cur = self.coll_d.find_one({'user_data.username': username,
                                    'user_data.user_id': user_id,
                                    'file.filename': filename,
                                    'file.user_dir': user_dir})
        if cur is None:
            return 'There is no such file in this directory'
        one_dir = cur['file']['sys_dir']
        sys_dir = self.directory + one_dir
        del_path = sys_dir + '/' + cur['file']['filename']
        os.remove(del_path)
        self.coll_d.delete_one({'user_data.username': username,
                            'user_data.user_id': user_id,
                            'file.filename': filename,
                            'file.user_dir': user_dir})

    # Добавление нужных директорий в основное поле с директориями,
    # поле нужно для выводе всех директорий, если понадобится.
    def add_way(self, username, user_id, pathway):
        new_pathway = '/' + username + pathway
        tmp = self.coll_d.find_one({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file': {}})
        ways = tmp['pathways']
        s = set(ways)
        s.add(new_pathway)
        ways = list(s)
        self.coll_d.update({'user_data.username': username,
                            'user_data.user_id': user_id,
                            'file': {}
                            },
                           {'$set':
                                {'pathways': ways}
                            })

    # Берем всех и выводим их
    def get_all(self):
        all_d = self.coll_d.find()
        for d in all_d:
            print d

    # Поиск файла по директории, проверяя тот ли это пользователь с помощью двух идентифкаторов username и user_id
    def find_files_in_dirs(self, username, user_id, user_dir):
        user_dir = '/' + user_dir
        files = {}

        tmp = self.coll_d.find({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': user_dir})
        for i in tmp:
            files[i['file']['filename']] = i['file']['sys_dir'][1:] + '/' + i['file']['filename']
        return files

    # Получение всех директорий, котрые есть у от той, в которой он находится, чтобы все вывести.
    # нужно вводить полную директорию нахождения пользователя и тогда метод будет выдевать следующие
    # возможные директории для прохождения
    def get_folder(self, username, user_id, user_dir):
        tmp = self.coll_d.find_one({'user_data.username': username,
                                    'user_data.user_id': user_id,
                                    'file': {}
                                    })
        paths = tmp['pathways']
        new_paths = set()
        sep_dir = user_dir.split('/')
        d = {}
        for path in paths:
            if user_dir in path:
                path = path.split('/')
                try:
                    count = path.index(sep_dir[-1])
                    if len(path)-count != 1:
                        new_paths.add(path[count+1])
                except ValueError as e:
                    pass
        for it in new_paths:
            d[it] = user_dir + '/' + it
        return d

    ''' Данный метод реализует подачу директорий пользователю и формате дикт
    на вход подуется имя пользователя его уникальный номер и путь, в который он хочет попасть.
    метод проверяет есть ли такой путь в БД и выдает словарь с ключами возможных переходов и 
    ссылками на эти переходы в значениях.
    Если указанного путя не существует, то пользователь получает сообщение об ошибке.    
    '''
    def get_dir(self, username, user_id, pathway):
        sample = self.coll_d.find_one({'user_data.username': username,
                                       'user_data.user_id': user_id,
                                       'file': {}})
        new_path = '/' + pathway
        tmp = sample['pathways']
        if new_path in tmp:
            d = OrderedDict()
            tmp = ''
            sep_path = pathway.split('/')
            for p in sep_path:
                if p:
                    tmp += p
                    d[p] = tmp
                    tmp += '/'
            return d
        else:
            return 'There is no such directory'

    # Смена имени директории. Для смены имени нужны все директории в который есть эта директория и их замена этого
    # имени на новое име созданное пользователем.
    def change_dir_name(self, username, user_id, old_user_dir, new_dir_name):
        if username == old_user_dir:
            return 'This directory can not be modified'
        reg = old_user_dir
        c = []
        old_way = old_user_dir.rpartition('/')
        sample = self.coll_d.find({'user_data.username': username,
                                   'user_data.user_id': user_id,
                                   'file.user_dir': {'$regex': reg}})
        count = self.coll_d.find({'user_data.username': username,
                                  'user_data.user_id': user_id,
                                  'file.user_dir': {'$regex': reg}}).count()

        for sm in sample:
            tmp = sm['file']['user_dir']
            tmp_1 = tmp.split('/')
            index = tmp_1.index(old_way[-1])
            tmp_1[index]=new_dir_name
            tmp = '/'.join(tmp_1)
            c.append(tmp)
        for i in c:
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': {'$regex': reg}},
                               {'$set': {
                                   'file.user_dir': i
                               }
                               })
        sample = self.coll_d.find_one({'user_data.username': username,
                                    'user_data.user_id': user_id,
                                    'file':{}})
        tmp = sample['pathways']
        tm = []
        for sm in tmp:
            sm_1 = sm.split('/')
            try:
                index = sm_1.index(old_way[-1])
                sm_1[index] = new_dir_name
                sm = '/'.join(sm_1)
            except Exception:
                pass
            tm.append(sm)

        if tm:
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file':{}},
                                {'$set': {
                                    'pathways': tm
                                    }
                                })
        if count == 0 and len(tmp) == 1:
            return 'Directory with this name does not exist'

    def rename_file(self, username, user_id, user_dir, old_filename, new_filename):
        user_dir = '/' + user_dir
        sample = self.coll_d.find_one({'user_data.username': username,
                                       'user_data.user_id': user_id,
                                       'file.user_dir': user_dir,
                                       'file.filename': old_filename})
        tmp = sample['file']['filename']
        old_extension = tmp.rpartition('.')[-1]
        new_extension = new_filename.rpartition('.')[-1]
        if old_extension == new_extension:
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': user_dir,
                                'file.filename':old_filename},
                               {'$set': {'file.filename': new_filename}})
            file_path = self.directory + sample['file']['sys_dir'] + '/'
            os.rename(file_path + tmp, file_path + new_filename)
        else:
            ans = 'You can not change the extension file' + old_extension + 'to an extension' + new_extension
            return  ans


    # Удаление директории из основной ячейки и, если есть файлы лежащие в этой директории, то и удаление
    # их.(Пока только из бд.
    # !!!!!из системы удаление не происходит!!!!!
    def delete_dir(self, username, user_id, name_dir):
        tmp = self.coll_d.find_one({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file':{}})
        new_ways = []
        ways = tmp['pathways']
        for way in ways:
            if name_dir not in way:
                new_ways.append(way)
        if len(ways) == len(new_ways):
            return 'This folder does not exist'
        self.coll_d.update({'user_data.username': username, 'user_data.user_id': user_id},
                                {'$set':
                                     {'pathways': new_ways}
                                 })
        reg = name_dir
        sample = self.coll_d.find({'user_data.username': username,
                                 'user_data.user_id': user_id,
                                 'file.user_dir': {'$regex': reg}})

        for samp in sample:
            sys_path = samp['file']['sys_dir']
            sys_path = self.directory + sys_path
            del_path = sys_path + '/' + samp['file']['filename']
            os.remove(del_path)
        self.coll_d.delete_many({'user_data.username': username,
                                 'user_data.user_id': user_id,
                                 'file.user_dir': {'$regex': reg}})



    def del_all(self):
        self.coll_d.remove(None)
        return 'del all'

    def create_folder(self, username, user_id, new_folder):
        sample = self.coll_d.find_one({'user_data.username': username,
                                       'user_data.user_id': user_id,
                                       'file': {}})
        new_folder = '/' + new_folder
        path = sample['pathways']
        if new_folder in path:
            return 'This folder already exists'
        s = set(path)
        s.add(new_folder)
        path = list(s)
        self.coll_d.update({'user_data.username': username,
                            'user_data.user_id': user_id,
                            'file': {}},
                           {'$set': {
                               'pathways': path
                           }
                           })

    def delete_user(self, username, user_id):
        sample = self.coll_d.find({'user_data.username':username,
                                   'user_data.user_id':user_id})
        for cur in sample:
            if cur['file']['sys_dir']:
                one_dir = cur['file']['sys_dir']
                sys_dir = self.directory + one_dir
                del_path = sys_dir + '/' + cur['file']['filename']
                os.remove(del_path)
                os.removedirs(sys_dir)
        self.coll_d.delete_many({'user_data.username': username,
                                'user_data.user_id': user_id})


b = UsersData()

f = True
if f:
    b.del_all()
    b.create_dir_for_user('admin', 1)
    b.create_dir_for_user('ihgorek', 2)
#else:
#    b.add_file('admin', 1, 'words.txt', 'admin')
 #   b.create_folder('admin', 1, 'admin/tor')
 #  b.add_file('admin', 1, 'users.pdf', 'admin/tor')

#b.add_file('admin', 1, 'words.txt', 'admin')
#b.add_file('admin', 1, 'words.txt', 'admin')
# b.create_dir_for_user('eva', 122)
#print b.add_file('admin', 1, 'words.txt', 'admin/dai')
# b.get_all()
# b.add_way('adam', 234, '/new')
# b.add_way('adam', 234, '/new/song')
# b.add_way('adam', 234, '/new/pic')
# print b.get_ways('adam', 234)
# b.delete_dir('adam', 234, '/new/ma/mo')
# print b.change_dir_name('admin', 1, 'admin/my', 'mo')
# t = b.find_files_in_dirs('admin', 1,'admin')
# for ti in t:
#     print ti
#b.get_all()
#print b.delete_dir('admin',1,'admin/me')
#b.del_file('admin',1,'words.txt','admin/ade')
#print b.get_dir('admin',1,'admin/admi')
#b.rename_file('ihgorek',2,'ihgorek','words.txt','file.txt')
b.delete_user('ihgorek',2)
b.get_all()


