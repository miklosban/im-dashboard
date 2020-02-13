from flask import json, session
from app.settings import cred_db_url
from app.db import DataBase


def _get_creds_db():
    db = DataBase(cred_db_url)
    if db.connect():
        if not db.table_exists("credentials"):
                db.execute("CREATE TABLE credentials(userid VARCHAR(255), serviceid VARCHAR(255), data LONGBLOB)")
    else:
        raise Exception("Error connecting DB: %s" % cred_db_url)
    return db

def get_cred(serviceid):
    db = _get_creds_db()
    res = db.select("select data from credentials where userid = %s and serviceid = %s", (session["userid"], serviceid))
    db.close()

    data = {}
    if len(res) > 0:
        data = json.loads(res[0][0])

    return data

def write_creds(serviceid, data):
    db = _get_creds_db()
    str_data = json.dumps(data)
    db.execute("replace into credentials (data, userid, serviceid) values (%s, %s, %s)", (str_data, session["userid"], serviceid))
    db.close()

def delete_cred(serviceid):
    db = _get_creds_db()
    db.execute("delete from credentials where userid = %s and serviceid = %s", (session["userid"], serviceid))
    db.close()