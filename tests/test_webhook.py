# tests/test_webhook.py
import unittest

class TestWebhookImport(unittest.TestCase):
    def test_import_webhook(self):
        import line_webhook
        self.assertTrue(hasattr(line_webhook, 'WebhookHandler'))
        self.assertTrue(hasattr(line_webhook, 'run'))
