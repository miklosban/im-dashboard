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
import xmltodict

from app.cred import Credentials
from mock import patch, MagicMock
from urllib.parse import urlparse


def read_file_as_string(file_name):
    tests_path = os.path.dirname(os.path.abspath(__file__))
    abs_file_path = os.path.join(tests_path, file_name)
    return open(abs_file_path, 'r').read()


class TestCredentials(unittest.TestCase):
    """
    Class to test the Credentials class
    """

    def setUp(self):
        creds = Credentials("sqlite:///tmp/creds.db")
        res = creds._get_creds_db()
        str_data = '{"project": "project_name"}'
        res.execute("replace into credentials (data, userid, serviceid) values (%s, %s, %s)",
                    (str_data, "user", "serviceid"))
        res.close()

    def tearDown(self):
        os.unlink("/tmp/creds.db")

    def test_get_cred(self):
        creds = Credentials("sqlite:///tmp/creds.db")
        res = creds.get_cred("serviceid", "user")
        self.assertEquals(res, {'project': 'project_name'})


if __name__ == '__main__':
    unittest.main()
