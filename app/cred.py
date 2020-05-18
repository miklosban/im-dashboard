from flask import json, session
from app.db import DataBase


class Credentials:

    def __init__(self, cred_db_url):
        self.cred_db_url = cred_db_url

    def _get_creds_db(self):
        db = DataBase(self.cred_db_url())
        if db.connect():
            if not db.table_exists("credentials"):
                db.execute("CREATE TABLE credentials(userid VARCHAR(255), serviceid VARCHAR(255), data LONGBLOB)")
        else:
            raise Exception("Error connecting DB: %s" % self.cred_db_url)
        return db

    def get_cred(self, serviceid):
        db = self._get_creds_db()
        res = db.select("select data from credentials where userid = %s and serviceid = %s",
                        (session["userid"], serviceid))
        db.close()

        data = {}
        if len(res) > 0:
            data = json.loads(res[0][0])

        return data

    def write_creds(self, serviceid, data):
        db = self._get_creds_db()
        str_data = json.dumps(data)
        db.execute("replace into credentials (data, userid, serviceid) values (%s, %s, %s)",
                   (str_data, session["userid"], serviceid))
        db.close()

    def delete_cred(self, serviceid):
        db = self._get_creds_db()
        db.execute("delete from credentials where userid = %s and serviceid = %s", (session["userid"], serviceid))
        db.close()
