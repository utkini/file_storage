# <p align="center">File storage
 
<p align="center">A simple, but extensible Python 
implementation for the File storage.

<p align="center">This project shows how you can use this API on the
example of File storage.

  * [Description.](#description)
  * [Deploy.](#deploy)

  
### Description.

This project shows how you can use the [File-storage-API](https://github.com/ihgorek/File-Storage-API).

### Deploy.

This service works with Python 2.7

In order to deploy this service at home. You need to write the following commands in the terminal

```
$ sudo apt-get install python-virtualenv python-pip
$ virtualenv env
$ source env/bin/activate
$ git clone https://github.com/ihgorek/file_storage.git
$ cd file_storage/app
$ pip install -r requirements.txt 
```
All the necessary libraries for the API are installed.

Api works with the MongoDB database on the local computer.
You need to [install MongoDB](https://docs.mongodb.com/manual/installation/)
to your computer.
After installing the database on your computer and launching it, 
service is ready to work.

In order to start the service you will need to install Nginx.
```
$ sudo apt-get install nginx
$ sudo rm /etc/nginx/sites-enabled/default
$ sudo touch /etc/nginx/sites-available/flask_settings
$ sudo ln -s /etc/nginx/sites-available/flask_settings /etc/nginx/sites-enabled/flask_settings
```
And now we open the file `nano /etc/nginx/sites-enabled/flask_settings` 
and write this code to it.

```
server {
        location / {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
        }
}
```
And restart Nginx `sudo /etc/init.d/nginx restart`

Then go to the folder with our project
`./file_storage/app` and write this command
```
$ gunicorn __init__:app
```

The server is deployed and ready to use. 

Thank you.


