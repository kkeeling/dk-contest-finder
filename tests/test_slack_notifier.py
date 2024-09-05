import unittest
from unittest.mock import MagicMock
from src.slack_notifier import SlackNotifier
from slack_sdk.errors import SlackApiError

class TestSlackNotifier(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.notifier = SlackNotifier(client=self.mock_client)

    def test_send_notification(self):
        self.mock_client.chat_postMessage.return_value = {"ok": True}

        result = self.notifier.send_notification("Test message")

        self.mock_client.chat_postMessage.assert_called_once_with(
            channel="__dk_contests",
            text="Test message"
        )
        self.assertTrue(result["ok"])

    def test_notify_contest(self):
        self.mock_client.chat_postMessage.return_value = {"ok": True}

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

        self.mock_client.chat_postMessage.assert_called_once()
        call_args = self.mock_client.chat_postMessage.call_args[1]
        self.assertEqual(call_args['channel'], "__dk_contests")
        self.assertIn("Test Contest", call_args['text'])
        self.assertIn("$10", call_args['text'])
        self.assertIn("$100", call_args['text'])
        self.assertIn("5", call_args['text'])
        self.assertIn("10", call_args['text'])
        self.assertIn("20.00%", call_args['text'])
        self.assertIn("https://www.draftkings.com/draft/contest/12345", call_args['text'])
        self.assertTrue(result["ok"])

    def test_rate_limiting(self):
        self.mock_client.chat_postMessage.side_effect = [
            SlackApiError(message="", response=MagicMock(status_code=429, headers={'Retry-After': '1'})),
            {"ok": True}  # Successful on second attempt
        ]

        with self.assertLogs(level='WARNING') as log:
            result = self.notifier.send_notification("Test message")

        self.assertEqual(self.mock_client.chat_postMessage.call_count, 2)
        self.assertIn("Rate limited. Retrying in 1 seconds.", log.output[0])
        self.assertTrue(result["ok"])

    def test_test_connection(self):
        self.mock_client.auth_test.return_value = {'ok': True, 'bot_id': 'test_bot'}

        result = self.notifier.test_connection()

        self.assertTrue(result)
        self.mock_client.auth_test.assert_called_once()

if __name__ == '__main__':
    unittest.main()
