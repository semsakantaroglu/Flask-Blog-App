## Yazılım Bilimi Blog developed with Python, Flask and Mysql Database

Install Flask by running command:
```
pip install Flask
```
### Mysql Database Configuration

Create tables named users and articles with the following fields;

Users
```
id ---> Auto Increment and Primary Key
name ---> Text
username ----> Text
email ----> Text
password ---> Text
```

Articles title,author,body
```
id ---> Auto Increment and Primary Key
title ---> Text
author ----> Text
body ----> Text
created_date ---> Timestamp
```
Edit these rows in blog.py with your username and password of Mysql
```python
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
```

#### That's it! Happy Coding!
