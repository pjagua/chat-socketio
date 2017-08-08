import pymysql
import pymysql.cursors



#Initialize DB object
db = pymysql.connect(
    user='root',
    password='testpass',
    host='db',
    database='chatapp',
)

# Initiallize Data Model if not already initialized
db.cursor().execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        username varchar(16),
        password varchar(96),
        salt varchar(16)
        )ENGINE=InnoDB''')

db.cursor().execute('''CREATE TABLE IF NOT EXISTS messages (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        sid INT UNSIGNED,
        rid INT UNSIGNED,
        message varchar(512),
        attributes JSON NOT NULL,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY SEND_INDEX (sid) REFERENCES accounts (id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        FOREIGN KEY RECV_INDEX (rid) REFERENCES accounts (id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
        )ENGINE=InnoDB''')


###
# TODO: Move Database operations here
