import os
import json
import hashlib
from binascii import hexlify
from binascii import a2b_base64

from .database import db

## Helper Functions

def chk_user(username):
    if not username:
        raise Exception("Username is empty\n")

    with db.cursor() as cursor:
        sql = "SELECT `id` FROM `accounts` WHERE `username`=%s"
        cursor.execute(sql, (username))
        result = cursor.fetchone()
        if result:
            return result[0]
    raise Exception("Failed to get id for {0}".format(username))

def useradd(user, passwd, salt):
    with db.cursor() as cursor:
        sql = "INSERT INTO `accounts` (`username`, `password`, `salt`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user, passwd, salt))
        result = cursor.fetchone()
    db.commit()
    return result

def salt_pass(passwd, salt=None):

    if passwd:
        try:
            if not salt:
                salt = hexlify(os.urandom(8))
        except Exception as e:
            raise Exception("failed to salt password: {0}".format(e))
        else:
            return hexlify(hashlib.pbkdf2_hmac("sha256", hexlify(passwd.encode("utf8")), salt, 100000)), salt
    raise Exception("Password is empty, failed to salt password: {0}".formtat(salt))


def user_auth(uid, passwd):

    if not passwd:
        raise Exception("Password is empty")

    with db.cursor() as cursor:
        sql = "SELECT `salt`, `password` FROM `accounts` WHERE `id`=%s"
        cursor.execute(sql, (uid))
        result = cursor.fetchone()

    try:
        prov_pass = salt_pass(passwd, result[0].encode("utf8"))
    except Exception as e:
        raise Exception("Failed to calculate password for authentication: {0}".format(e))
    else:
        if prov_pass[0]  == result[1].encode("utf8"):
            return True
        raise Exception("Failed to Authenticate: hashes do not match {0} - {1}".format(prov_pass[0], result[1]))
 

def store_msg(msg, s_user, r_user, attrib=None):
    if not msg and not s_user and not r_user:
        raise Exception("message arguments are not complete")

    try:
        sid = chk_user(s_user)
        rid = chk_user(r_user)
    except Exception as e:
        raise Exception("Failed to find user in Database: {0}".format(e))
    else:
        with db.cursor() as cursor:
            sql = "INSERT INTO `messages` (`sid`, `rid`, `message`, `attributes`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (sid, rid, msg, json.dumps(attrib)))
            db.commit()
            cursor.close()
        return msg_fetch(sid, rid)

def msg_fetch(sid, rid, page=None, limit=None):
    if page and limit:
        page = page * limit
    else:
        page = 0

    if not limit:
        limit = 10**18

    with db.cursor() as cursor:
        sql = "SELECT `date`, `message`, `attributes`, `id` FROM `messages` WHERE `sid` AND `rid` IN (%s, %s) ORDER BY UNIX_TIMESTAMP(date) DESC LIMIT %s, %s"
        cursor.execute(sql, (sid, rid, int(page), int(limit)))
        result = cursor.fetchall()
        cursor.close()

    return result


def cleanup():
    """
    TODO:
    Perform Cleanup
    """
    pass
