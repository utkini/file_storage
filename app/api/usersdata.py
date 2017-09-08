# coding=utf-8
import hashlib
import os
import shutil
from collections import OrderedDict

from pymongo import MongoClient
import pymongo


class UsersData(object):
    """This is UsersData class.

    This class is intended for basic user actions
    Methods:
        createDirForUser
        addFile
        renameFile
        delFile
        findFilesInDirs
        addWay
        createFolder
        getFolder
        getDir
        changeDirName
        deleteDir
        deleteUser
        getAll
        delAll
        """

    def __init__(self):
        """Creating a link to the MongoDB

        :return: UserData object.
        """
        self.directory = '/home/user1/my_flask_app/users'
        self.TEXT = {'txt', 'doc', 'docx', 'docm', 'dotm', 'dotx', 'pdf',
                     'xls', 'xlsx', 'xlsm', 'xltx', 'xlt', 'xltm', 'pptx',
                     'ppt', 'ppsx', 'pps', 'potx', 'pot', 'ppa', 'ppam'}
        self.PIC = {'jpg', 'jpeg', 'tif', 'tiff', 'png', 'gif', 'bmp'}
        self.SONG = {'wav', 'mp3', 'wma', 'ogg', 'aac', 'flac'}
        self.VIDEO = {'avi', 'mkv', 'mp4', 'mpeg'}
        with MongoClient('localhost', 27017) as mongo:
            db = mongo.db_storage
            self.coll_d = db.coll_data

    def create_dir_for_user(self, username, user_id):
        """Create a root folder for the user

        Use this method to create a user by creating the user's root folder and
        adding the user to the database.
        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :return: If True -> None. if False - >  Exception
        """
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

    def add_file(self, username, user_id, filename, user_dir=''):
        """Adding a file to the database and creating a directory to write it to the server

        This method implements adding a file to the database and creating directories on the server
        and directories for the user to store this file.
        Before adding the file to the database and saving it to the server, the method checks the file extension.
        At the moment, you can save almost all files such as TEXT, PICTURE and SONG
        If a file exists for a given user path, the method overwrites the file by changing its name
        Example:
            words.txt
            words(1).txt
            words(2).txt
        On the server, the file is saved in folders created using the md5 algorithm.
        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param filename: String : User file name
        :param user_dir: String : If None - > saves the file to the root folder of the user
        :return: dict {filename: filename, file_dir: file dir in system}.
        If False - > The extension of these files are not supported by this system.
        """
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
            except OSError as e:
                print str(e)
        sys_dir = new_dir
        tmp = new_filename.rpartition('.')
        format_file = tmp[-1]
        if format_file in self.TEXT or \
                        format_file in self.PIC or \
                        format_file in self.SONG or \
                        format_file in self.VIDEO:
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
                                        'file': {}})
            s = cur['pathways']
            s = set(s)
            s.add(new_user_dir)
            s = list(s)
            self.coll_d.update({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file': {}},
                               {'$set': {'pathways': s}})
            d = {'file_dir': file_dir, 'filename': new_filename}
            return d
        else:
            return 'The extension of these files are not supported by this system.'

    def rename_file(self, username, user_id, user_dir, old_filename, new_filename):
        """Use this method to change the filename

        This method implements the renaming of the file in the database and in the system
        along the way from the database.

        If the requested file does not exist, the method returns an error message:
        "Such file does not exist"

        !Important! In the method, the filename is supplied with an extension and, if the extensions do not coincide
        the file to be modified, and the proposed file, the method will return an error message:
        "You can not change the extension file *** to an extension ***"

        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param user_dir: String : User directory in which he will save the file
        :param old_filename: String : The name of the old file
        :param new_filename: String :
        :return: None. If false - > error message
        """
        try:
            user_dir = '/' + user_dir
            sample = self.coll_d.find_one({'user_data.username': username,
                                           'user_data.user_id': user_id,
                                           'file.user_dir': user_dir,
                                           'file.filename': old_filename})
            tmp = sample['file']['filename']
            old_extension = tmp.rpartition('.')[-1]
            new_extension = new_filename.rpartition('.')[-1]
            if old_extension == new_extension:
                samp = self.coll_d.find({'user_data.username': username,
                                         'user_data.user_id': user_id,
                                         'file.user_dir': user_dir,
                                         'file.filename': {'$regex': new_filename}
                                         }).count()
                if samp != 0:
                    sep_filename = new_filename.rpartition('.')
                    filename = sep_filename[0] + '(' + str(samp) + ')'
                    new_filename = filename + '.' + sep_filename[-1]
                self.coll_d.update({'user_data.username': username,
                                    'user_data.user_id': user_id,
                                    'file.user_dir': user_dir,
                                    'file.filename': old_filename},
                                   {'$set': {'file.filename': new_filename}})
                file_path = self.directory + sample['file']['sys_dir'] + '/'
                os.rename(file_path + tmp, file_path + new_filename)
            else:
                ans = 'You can not change the extension file' + old_extension + 'to an extension' + new_extension
                return ans
        except Exception:
            return 'Such file does not exist'

    def del_file(self, username, user_id, filename, user_dir):
        """Use this method to delete a file from the database and the system

        Deleting a file from the database and the system by storing this file in the system.
        
        If the requested file does not exist, the method displays a message:
        "There is no such file in this directory"
        
        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param filename: String :
        :param user_dir: String : The directory of the user in which he wants to delete the file
        :return: None. If False - > error message
        """
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

    def find_files_in_dirs(self, username, user_id, user_dir):
        """Search all files in this directory

        Search for a file by directory, checking whether it's the user with
        using two identifiers username and user_id
        displays a file and its location, for downloading
        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param user_dir:
        :return: dict { filename: filename, file_path : file path in system }
        """
        user_dir = '/' + user_dir
        files = {}

        tmp = self.coll_d.find({'user_data.username': username,
                                'user_data.user_id': user_id,
                                'file.user_dir': user_dir})
        for i in tmp:
            files[i['file']['filename']] = i['file']['sys_dir'][1:] + '/' + i['file']['filename']
        return files

    def add_way(self, username, user_id, pathway):
        """Adding the necessary directories to the main field with directories,

        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param pathway: String :
        :return: None
        """
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

    def create_folder(self, username, user_id, new_folder):
        """This method is used to create a new folder for the user

        Creates a folder for the user in which you can store data. This method is also
        creates dependencies between the rest of the folders, creating a "tree".
        
        If the user in the directory tries to create a folder with a duplicate name,
        then the method returns an error message:
        "This folder exist exist"

        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param new_folder: String : Name new folder
        :return: None. If false - > error message
        """
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

    def get_folder(self, username, user_id, user_dir):
        """Use this method to get all the folders in this directory

        Getting all folders with directories that are relative to the directory in which the user is located.
        you need to enter the full directory of the user's location and then the method will produce the following
        Possible files with directories for the dictionary to go deep
        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param user_dir: String :
        :return: dict {name folder: name folder, folder path: folder path }
        """
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
                    if len(path) - count != 1:
                        new_paths.add(path[count + 1])
                except ValueError as e:
                    pass
        for it in new_paths:
            d[it] = user_dir + '/' + it
        return d

    def get_dir(self, username, user_id, pathway):
        """Use this method to retrieve all the parent directories

        This method implements the submission of directories to the user in the format of the ordered dict
        The input is given the username of its unique number and the path to which it wants to get.
        The method checks whether there is such a path in the database and all parents with references to them,
        for further transfer to the user.
        
        If the specified directory does not exist, the user receives an error message:
        "There is no such directory"
        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param pathway: String
        :return: OrderedDict { name directory: the path of this directory}. If false - > error message
        """
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

    def change_dir_name(self, username, user_id, old_user_dir, new_dir_name):
        """Use this method to change the directory name

        You can change all directories except the parent "username".
        The new directory name replaces the old one in the database everywhere and gives None if
        all the actions are successful.
        To change the name you need all the directories in which there is this directory and their replacement
        the name of the new user created by the user.

        If the directory does not exist, the method will return an error message:
        "Directory with this name does not exist"

        If the user tries to change the feed folder, then he will receive an error message:
        "This directory can not be modified"

        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param old_user_dir: String : The name of the directory you want to change
        :param new_dir_name: String : New name directory
        :return: None. If false ->    error message
        """
        if username == old_user_dir:
            return 'This directory can not be modified'
        if new_dir_name == '':
            return 'You must write a new directory name'
        if new_dir_name == old_user_dir.rpartition('/')[-1]:
            return 'You can not change the directory name to exactly the same'
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
            tmp_1[index] = new_dir_name
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
                                       'file': {}})
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
                                'file': {}},
                               {'$set':
                                   {
                                       'pathways': tm
                                   }
                               })
        if count == 0 and len(tmp) == 1:
            return 'Directory with this name does not exist'

    def delete_dir(self, username, user_id, name_dir):
        """Use this method to delete a directory

        Deleting a directory from the main cell and, if there are files lying in this directory, then deleting
        them from the database and the system
        
        If the deleted directory does not exist, the method will return an error message:
        "This folder does not exist"

        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :param name_dir: String : The name of the directory you want to delete
        :return: None. If false - > error message
        """
        tmp = self.coll_d.find_one({'user_data.username': username,
                                    'user_data.user_id': user_id,
                                    'file': {}})
        if name_dir == '':
            return 'This field must be filled'
        new_ways = []
        ways = tmp['pathways']
        for way in ways:
            if name_dir != way:
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
                                   'file.user_dir': reg})

        for samp in sample:
            sys_path = samp['file']['sys_dir']
            sys_path = self.directory + sys_path
            del_path = sys_path + '/' + samp['file']['filename']
            os.remove(del_path)
        self.coll_d.delete_many({'user_data.username': username,
                                 'user_data.user_id': user_id,
                                 'file.user_dir': reg})

    def delete_user(self, username, user_id):
        """Delete the user by this user ID and name.

        Removes all user folders on the system, and all database entries associated with this user.

        If an error occurs when the user is deleted, this method returns an error message
        "Oops"
        :param username: Integer or String : Unique username
        :param user_id: Integer : Unique  user ID
        :return: None. If false -> "Oops"
        """
        try:
            shutil.rmtree(self.directory + '/' + username)
            self.coll_d.delete_many({'user_data.username': username,
                                     'user_data.user_id': user_id})
        except Exception:
            return 'Oops'

    def get_all(self):
        """Use this method to view all records in the database

        :return: mongodb dict   {
                                'user_data':
                                    {
                                        'username': username,
                                        'user_id': user_id
                                    },
                                    'file':
                                        {
                                            'filename': new_filename,
                                            'user_dir': new_user_dir,
                                            'sys_dir': sys_dir
                                        }
                                }
        ___________________     and
                                {
                                'user_data':
                                    {
                                        'username': username,
                                        'user_id': user_id
                                    },
                                'file': {},
                                'pathways': [user_dir]
                                }

        """
        all_d = self.coll_d.find()
        for d in all_d:
            print d

    def del_all(self):
        """Use this method to completely clean the database

        :return: String : del all
        """
        self.coll_d.remove(None)
        return 'del all'


def main():
    b = UsersData()

    f = False
    if f:
        b.del_all()
    b.get_all()
    # b.create_dir_for_user('admin', 1)
    # b.create_dir_for_user('ihgorek', 2)
    # else:
    #    b.add_file('admin', 1, 'words.txt', 'admin')
    #   b.create_folder('admin', 1, 'admin/tor')
    #  b.add_file('admin', 1, 'users.pdf', 'admin/tor')
    # b.get_all()
    # print b.delete_dir('admin',1,'admin/me')
    # b.del_file('admin',1,'words.txt','admin/ade')
    # print b.get_dir('admin',1,'admin/admi')
    # b.rename_file('ihgorek',2,'ihgorek','words.txt','file.txt')
    # b.delete_user('ihgorek',2)
    # b.create_folder('admin',1,'ma')
    # b.create_folder('admin',1,'mat')
    # b.delete_dir('admin',1,'/admin/ma')


if __name__ == "__main__":
    main()
