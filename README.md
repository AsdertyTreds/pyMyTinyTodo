# pyMyTinyTodo
Simple way to manage todo list in AJAX style.
Written in Python and js jQuery.
Data stored in SQLite, MySQL, PosgreSql, MSSql, Oracle database.
Distributed under the GNU GPL License

This is a copy and continuation of the project https://mytinytodo.net (author Max Pozdeev), written in php language

System requirements

    Python~=3.7
    flask~=1.1.2
    pytz~=2020.5
    pymysql~=1.0.2
    psycopg2~=2.8.6
    pyodbc~=4.0.30
    cx-Oracle~=8.1.0
    Flask-SQLAlchemy~=2.4.4
    SQLAlchemy~=1.3.22


Tested in browsers: Chrome 85, Safari 14, Firefox 80, IE v11

How to install myTinyTodo

    Download release archive
    Unpack
    Make enviroment in directory pymytinytodo
    > python -m venv venv
    > pip install -r requirements.txt
    > python main.py
    Go to http://127.0.0.1:5000
    Make sure config file 'db/config.json' is writable for webserver.
    Select and specify settings of database you prefer in start page. 
    For sqlite usage make sure that database file 'db/mtt.db' is writable for webserver.
    To protect your tasks from modification by the others you may specify password in settings.

Update to new version

    