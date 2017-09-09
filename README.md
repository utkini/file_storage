## <p align="center">File storage
 
<p align="center">A simple, but extensible Python 
implementation for the File storage.

<p align="center">This project shows how you can use this API on the
example of File storage.

  * [Description.](#description)
  * [Getting started.](#getting-started)
  * [Class Register.](#class-register)
  * [Class LogIn.](#class-login)
  * [Class UsersData.](#class-usersdata)
  
### Description.

Api consists of three classes: Register, LogIn and UsersData:

- [Register class](#class-register) is responsible for user registration;
- [LogIn class](#class-login) is responsible for identifying the user in the database's database system;
- [UsersData class](#class-usersdata) is responsible for all the work with files and user directories.

### Getting started.

This API works with Python 2.7

In order to start using the API, you need to download it to your project.

```
$ git clone https://github.com/ihgorek/File-Storage-API.git
$ cd File-Storage-API
$ pip install -r requirements.txt 
```
All the necessary libraries for the API are installed.

Api works with the MongoDB database on the local computer.
You need to [install MongoDB](https://docs.mongodb.com/manual/installation/)
to your computer.
After installing the database on your computer and launching it, 
API is ready to work.

### Class Register.

Register Class is responsible for adding the user to the database and obtaining 
the necessary information about the user at the time of registration, for further 
work. In this class 4 auxiliary methods and 2 basic methods.


### Class LogIn.

Login class is needed to identify the user on the system and update his data. 
The class contains 6 basic methods for dabot with the user.

### Class UsersData.

UsersData class is the main class. He does all the work with the user's files. 
Creates the necessary folders for storing files and updating them. All user files 
are stored in the directory that is in the **UPLOAD_FOLDER** variable in 
the `app/__init__.py` file and in the **directory** variable, which is in 
the `app/api/usersdata.py` file. All folders for storing files are created in this directory. 
To change the directory for saving files, you need to change these all 
variables in `/ __init__.py` and in `api/usersdata.py`