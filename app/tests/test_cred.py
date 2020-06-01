#! /usr/bin/env python
#
# IM - Infrastructure Manager
# Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os

from app.cred import Credentials


class TestCredentials(unittest.TestCase):
    """Class to test the Credentials class."""

    def tearDown(self):
        os.unlink('/tmp/creds.db')

    def test_get_cred(self):
        creds = Credentials("sqlite:///tmp/creds.db")
        res = creds._get_creds_db()
        str_data = '{"project": "project_name"}'
        res.execute("replace into credentials (data, userid, serviceid) values (%s, %s, %s)",
                    (str_data, "user", "serviceid"))
        res.close()

        res = creds.get_cred("serviceid", "user")
        self.assertEquals(res, {'project': 'project_name'})

    def test_write_creds(self):
        creds = Credentials("sqlite:///tmp/creds.db")
        creds.write_creds("serviceid", "user", {"project": "new_project"})
        res = creds.get_cred("serviceid", "user")
        self.assertEquals(res, {"project": "new_project"})

    def test_delete_creds(self):
        creds = Credentials("sqlite:///tmp/creds.db")
        creds.delete_cred("serviceid", "user")
        res = creds.get_cred("serviceid", "user")
        self.assertEquals(res, {})


if __name__ == '__main__':
    unittest.main()
