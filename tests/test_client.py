import unittest
from unittest.mock import patch, MagicMock

from roku.models import RokuDevice, RokuApp
from roku.client import RokuClient


class TestRokuClient(unittest.TestCase):

    def setUp(self):
        self.device = RokuDevice(name="Test Roku", ip="192.168.1.100")
        self.client = RokuClient(self.device)

    # ── keypress ──────────────────────────────────────────────

    @patch('roku.client.requests.post')
    def test_keypress_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.keypress('Home')
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            'http://192.168.1.100:8060/keypress/Home', timeout=3
        )

    @patch('roku.client.requests.post')
    def test_keypress_returns_false_on_non_200(self, mock_post):
        mock_post.return_value = MagicMock(status_code=404)
        result = self.client.keypress('Home')
        self.assertFalse(result)

    @patch('roku.client.requests.post')
    def test_keypress_returns_false_on_network_error(self, mock_post):
        import requests as req
        mock_post.side_effect = req.RequestException("timeout")
        result = self.client.keypress('Home')
        self.assertFalse(result)

    # ── get_apps ──────────────────────────────────────────────

    APPS_XML = (
        '<?xml version="1.0"?><apps>'
        '<app id="12" version="4.1.218">Netflix</app>'
        '<app id="2285" version="2.0.2">YouTube</app>'
        '<app id="13" version="4.7">Amazon Video</app>'
        '</apps>'
    )

    @patch('roku.client.requests.get')
    def test_get_apps_returns_list(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, text=self.APPS_XML)
        mock_get.return_value.raise_for_status = MagicMock()
        apps = self.client.get_apps()
        self.assertEqual(len(apps), 3)
        self.assertEqual(apps[0].name, 'Netflix')
        self.assertEqual(apps[0].app_id, '12')
        self.assertEqual(apps[0].version, '4.1.218')

    @patch('roku.client.requests.get')
    def test_get_apps_returns_empty_on_error(self, mock_get):
        mock_get.side_effect = Exception("network error")
        apps = self.client.get_apps()
        self.assertEqual(apps, [])

    # ── launch_app ────────────────────────────────────────────

    @patch('roku.client.requests.post')
    def test_launch_app_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        result = self.client.launch_app('12')
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            'http://192.168.1.100:8060/launch/12', timeout=3
        )

    @patch('roku.client.requests.post')
    def test_launch_app_failure(self, mock_post):
        import requests as req
        mock_post.side_effect = req.RequestException("refused")
        result = self.client.launch_app('12')
        self.assertFalse(result)

    # ── RokuDevice ────────────────────────────────────────────

    def test_device_base_url(self):
        self.assertEqual(self.device.base_url, 'http://192.168.1.100:8060')

    def test_device_str(self):
        self.assertIn('192.168.1.100', str(self.device))


class TestRokuApp(unittest.TestCase):

    def test_app_str(self):
        app = RokuApp(app_id='12', name='Netflix', version='4.1')
        self.assertEqual(str(app), 'Netflix')


if __name__ == '__main__':
    unittest.main()
