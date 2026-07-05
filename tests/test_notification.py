# tests/test_notification.py
import unittest
from unittest.mock import patch, MagicMock
from services.notification_service import NotificationService
from config.settings import Settings

class TestNotificationService(unittest.TestCase):
    def setUp(self):
        # Configure dummy credentials for testing
        self.orig_token = Settings.LINE_CHANNEL_ACCESS_TOKEN
        self.orig_user = Settings.LINE_USER_ID
        Settings.LINE_CHANNEL_ACCESS_TOKEN = "dummy_token"
        Settings.LINE_USER_ID = "dummy_user"

    def tearDown(self):
        Settings.LINE_CHANNEL_ACCESS_TOKEN = self.orig_token
        Settings.LINE_USER_ID = self.orig_user

    @patch('urllib.request.urlopen')
    @patch('time.sleep') # Mock sleep to make test run instantly
    def test_send_notification_success(self, mock_sleep, mock_urlopen):
        # Mock successful 200 OK response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"status": "ok"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        success = NotificationService.send_event_notification("test_event", "test@example.com")
        self.assertTrue(success)
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    @patch('time.sleep')
    def test_send_notification_failure_and_retry(self, mock_sleep, mock_urlopen):
        # Mock failed response (e.g. 500 Internal Error)
        mock_response = MagicMock()
        mock_response.getcode.return_value = 500
        mock_response.read.return_value = b'{"error": "failed"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Act
        success = NotificationService.send_event_notification("test_event", "test@example.com")
        
        # Should return False and try 2 times (initial + 1 retry)
        self.assertFalse(success)
        self.assertEqual(mock_urlopen.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    def test_send_notification_skipped_when_no_token(self):
        Settings.LINE_CHANNEL_ACCESS_TOKEN = None
        success = NotificationService.send_event_notification("test_event", "test@example.com")
        self.assertFalse(success)
