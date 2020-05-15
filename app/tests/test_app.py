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
        self.assertIn(b"infid", res.data)