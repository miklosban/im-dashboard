import unittest
from urllib.parse import urlparse
from app import create_app
from mock import patch, MagicMock

class IMDashboardTests(unittest.TestCase):

    oauth = MagicMock()

    def setUp(self):
        self.app = create_app(self.oauth)
        self.client = self.app.test_client()

    def get_response(self, url, params=None, **kwargs):
        resp = MagicMock()
        parts = urlparse(url)
        url = parts[2]
        params = parts[4]

        resp.status_code = 404
        resp.ok = False

        if url == "/im/infrastructures":
            resp.ok = True
            resp.status_code = 200
            resp.json.return_value = {"uri-list": [{"uri": "http://server.com/im/infrastructures/infid"}]}
        elif url == "/im/infrastructures/infid/state":
            resp.ok = True
            resp.status_code = 200
            resp.json.return_value = {"state": {"state": "configured", "vm_states": {"0": "configured"}}}
        elif url == "/im/infrastructures/infid/vms/0":
            resp.ok = True
            resp.status_code = 200
            resp.text = ""
            radl =   {
                        "class": "system",
                        "cpu.arch": "x86_64",
                        "cpu.count_min": 1,
                        "disk.0.image.url": "one://server.com/id",
                        "disk.0.os.name": "linux",
                        "id": "front",
                        "sttate": "configured",
                        "disk.0.os.credentials.username": "user",
                        "disk.0.os.credentials.password": "pass",
                        "memory.size_min": 536870912,
                        "net_interface.0.connection": "publica",
                        "net_interface.0.ip": "10.10.10.10",
                        "provider.type": "OpenNebula",
                        "provider.host": "server.com"
                    }
            resp.json.return_value = {"radl": [radl]}
        elif url == "/im/infrastructures/infid/vms/0/stop":
            resp.ok = True
            resp.status_code = 200

        return resp

    def put_response(self, url, params=None, **kwargs):
        resp = MagicMock()
        parts = urlparse(url)
        url = parts[2]
        params = parts[4]

        resp.status_code = 404
        resp.ok = False

        if url == "/im/infrastructures/infid/vms/0/stop":
            resp.ok = True
            resp.status_code = 200

        return resp

    def delete_response(self, url, params=None, **kwargs):
        resp = MagicMock()
        parts = urlparse(url)
        url = parts[2]
        params = parts[4]

        resp.status_code = 404
        resp.ok = False

        if url == "/im/infrastructures/infid/vms/0":
            resp.ok = True
            resp.status_code = 200

        return resp

    def login(self, avatar):
        self.oauth.session.authorized = True
        self.oauth.session.token = {'expires_in': 500, 'access_token': 'token'}
        account_info = MagicMock()
        account_info.ok = True
        account_info.json.return_value = {"sub": "userid", "name": "username"}
        self.oauth.session.get.return_value = account_info
        avatar.return_value = ""
        return self.client.get('/')

    def test_index_with_no_login(self):
        self.oauth.session.authorized = False
        res = self.client.get('/')
        self.assertEqual(302, res.status_code)
        self.assertIn('/login', res.headers['location'])

    @patch("app.utils.avatar")
    def test_index(self, avatar):
        res = self.login(avatar)
        self.assertEqual(200, res.status_code)

    @patch("app.utils.avatar")
    def test_settings(self, avatar):
        self.login(avatar)
        res = self.client.get('/settings')
        self.assertEqual(200, res.status_code)
        self.assertIn(b"https://appsgrycap.i3m.upv.es:31443/im", res.data)

    @patch("app.utils.getUserAuthData")
    @patch('requests.get')
    @patch("app.utils.avatar")
    def test_infrastructures(self, avatar, get, user_data):
        user_data.return_value = "type = InfrastructureManager; token = access_token"
        get.side_effect = self.get_response
        self.login(avatar)
        res = self.client.get('/infrastructures')
        self.assertEqual(200, res.status_code)
        self.assertIn(b'infid', res.data)
        self.assertIn(b'<span class="fas fa-server mr-2"></span>0', res.data)

    @patch("app.utils.getUserAuthData")
    @patch('requests.get')
    @patch("app.utils.avatar")
    def test_vm_info(self, avatar, get, user_data):
        user_data.return_value = "type = InfrastructureManager; token = access_token"
        get.side_effect = self.get_response
        self.login(avatar)
        res = self.client.get('/vminfo/infid/0')
        self.assertEqual(200, res.status_code)
        self.assertIn(b'Username: user', res.data)
        self.assertIn(b'Password: pass', res.data)

    @patch("app.utils.getUserAuthData")
    @patch('requests.put')
    @patch("app.utils.avatar")
    @patch("app.flash")
    def test_managevm_stop(self, flash, avatar, put, user_data):
        user_data.return_value = "type = InfrastructureManager; token = access_token"
        put.side_effect = self.put_response
        self.login(avatar)
        res = self.client.get('/managevm/stop/infid/0')
        self.assertEqual(302, res.status_code)
        self.assertIn('http://localhost/vminfo/infid/0', res.headers['location'])
        self.assertEquals(flash.call_args_list[0][0], ("Operation 'stop' successfully made on VM ID: 0", 'info'))

    @patch("app.utils.getUserAuthData")
    @patch('requests.delete')
    @patch("app.utils.avatar")
    @patch("app.flash")
    def test_managevm_delet(self, flash, avatar, delete, user_data):
        user_data.return_value = "type = InfrastructureManager; token = access_token"
        delete.side_effect = self.delete_response
        self.login(avatar)
        res = self.client.get('/managevm/terminate/infid/0')
        self.assertEqual(302, res.status_code)
        self.assertIn('http://localhost/infrastructures', res.headers['location'])
        self.assertEquals(flash.call_args_list[0][0], ("Operation 'terminate' successfully made on VM ID: 0", 'info'))