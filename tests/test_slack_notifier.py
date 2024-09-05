import unittest
from unittest.mock import patch, MagicMock
from src.slack_notifier import SlackNotifier
from slack_sdk.errors import SlackApiError

class TestSlackNotifier(unittest.TestCase):
    def setUp(self):
        self.notifier = SlackNotifier()

    @patch('src.slack_notifier.WebClient')
    def test_send_notification(self, mock_web_client):
        mock_client = MagicMock()
        mock_web_client.return_value = mock_client
        mock_client.chat_postMessage.return_value = {"ok": True}

        result = self.notifier.send_notification("Test message")

        mock_client.chat_postMessage.assert_called_once_with(
            channel="__dk_contests",
            text="Test message"
        )
        self.assertTrue(result["ok"])

    @patch('src.slack_notifier.WebClient')
    def test_notify_contest(self, mock_web_client):
        mock_client = MagicMock()
        mock_web_client.return_value = mock_client
        mock_client.chat_postMessage.return_value = {"ok": True}

        contest = {
            'id': '12345',
            'title': 'Test Contest',
            'entry_fee': 10,
            'total_prizes': 100,
            'current_entries': 5,
            'maximum_entries': 10,
            'highest_experience_ratio': 0.2
        }

        result = self.notifier.notify_contest(contest)

        mock_client.chat_postMessage.assert_called_once()
        call_args = mock_client.chat_postMessage.call_args[1]
        self.assertEqual(call_args['channel'], "test_channel")
        self.assertIn("Test Contest", call_args['text'])
        self.assertIn("$10", call_args['text'])
        self.assertIn("$100", call_args['text'])
        self.assertIn("5", call_args['text'])
        self.assertIn("10", call_args['text'])
        self.assertIn("20.00%", call_args['text'])
        self.assertIn("https://www.draftkings.com/draft/contest/12345", call_args['text'])
        self.assertTrue(result["ok"])

    @patch('src.slack_notifier.WebClient')
    def test_rate_limiting(self, mock_web_client):
        mock_client = MagicMock()
        mock_web_client.return_value = mock_client

        mock_client.chat_postMessage.side_effect = [
            SlackApiError(message="", response=MagicMock(status_code=429, headers={'Retry-After': '1'})),
            {"ok": True}  # Successful on second attempt
        ]

        with patch('time.sleep') as mock_sleep:
            result = self.notifier.send_notification("Test message")

        self.assertEqual(mock_client.chat_postMessage.call_count, 2)
        mock_sleep.assert_called_once_with(1)
        self.assertTrue(result["ok"])

    @patch('src.slack_notifier.WebClient')
    def test_test_connection(self, mock_web_client):
        mock_client = MagicMock()
        mock_web_client.return_value = mock_client

        mock_client.auth_test.return_value = {'ok': True, 'bot_id': 'test_bot'}

        result = self.notifier.test_connection()

        self.assertTrue(result)
        mock_client.auth_test.assert_called_once()

if __name__ == '__main__':
    unittest.main()
