import os
import sys
import json
import hashlib
from binascii import hexlify
from binascii import a2b_base64

## Helper Functions

def chk_user(username, db=None):
    if not username:
        raise Exception("Username is empty\n")

    col = ("id",)
    sql = {
           "FROM":"accounts",
           "WHERE":"username= '{0}'".format(username)
          }
    try:
        result = db.select_query(*col, **sql)
    except Exception as e:
        raise Exception("Failed to get id for {0}: {1}".format(username, e))
    else:
        if result:
            return result[0][0]
        else:
            raise RuntimeError("Failed to retrieve uid of user")

def useradd(user, passwd, salt, db=None):
    sql = {
           "INTO" : " `accounts` (`username`, `password`, `salt`)",
           "VALUES" : "('{0}', '{1}', '{2}')".format(user, passwd.decode("utf-8"), salt.decode("utf-8"))
          }
    try:
        result = db.insert(**sql)
    except Exception as e:
        raise RuntimeError(e)
    else:
        return result

def salt_pass(passwd, salt=None):

    if passwd:
        try:
            if not salt:
                salt = hexlify(os.urandom(8))
        except Exception as e:
            raise Exception("failed to salt password: {0}".format(e))
        else:
            print(type(salt), list(salt))
            return hexlify(hashlib.pbkdf2_hmac("sha256", hexlify(passwd.encode("utf8")), salt, 100000)), salt
    raise Exception("Password is empty, failed to salt password: {0}".format(salt))


def user_auth(uid, passwd, db=None):

    if not passwd:
        raise Exception("Password is empty")
    col = ("password", "salt")
    sql = {
           "FROM":"accounts",
           "WHERE":"`id`='{0}'".format(uid[0])
          }
    try:
        result = db.select_query(*col, **sql)
        prov_pass = salt_pass(passwd, result[0][1])
    except Exception as e:
        raise Exception("Failed to calculate password for authentication: {0}: {1}".format(result[0][0], e))
    else:
        if prov_pass[0]  == result[0][0]:
            return True
        raise Exception("Failed to Authenticate: hashes do not match {0} - {1}".format(prov_pass[0], result[0][0]))
 

def store_msg(msg, s_user, r_user, attrib=None, db=None):
    if not msg and not s_user and not r_user:
        raise Exception("message arguments are not complete")

    try:
        sid = chk_user(s_user, db)
        rid = chk_user(r_user, db)
    except Exception as e:
        raise Exception("Failed to find user in Database: {0}".format(e))
    else:
        try:
            sql = {
               "INTO" : " `messages` (`sid`, `rid`, `message`, `attributes`)",
               "VALUES" : "('{0}', '{1}', '{2}', '{3}')".format(sid, rid, msg, json.dumps(attrib))
               }
            result = db.insert(**sql)
        except Exception as sql_err:
            raise Exception("Failed to INSERT: {0}". format(sql_err))
        return msg_fetch(sid, rid, None, None, db)

def msg_fetch(sid, rid, page=None, limit=None, db=None):
    if page and limit:
        page = page * limit
    else:
        page = 0

    if not limit:
        limit = 10**18

    col = ("date", "message", "attributes", "id")
    sql = {
            "FROM":"messages",
            "WHERE":"`sid`='{0}' AND `rid`='{1}'".format(sid, rid),
            "ORDER BY":"date",
            "LIMIT":"{0}, {1}".format(int(page), int(limit))
          }

    return db.select_query(*col, **sql)


def cleanup():
    """
    TODO:
    Perform Cleanup
    """
    pass
