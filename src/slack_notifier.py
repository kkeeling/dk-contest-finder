import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

class SlackNotifier:
    def __init__(self, token=None, default_channel=None):
        self.token = token or os.environ.get("SLACK_BOT_TOKEN")
        if not self.token:
            raise ValueError("Slack bot token is required")
        self.client = WebClient(token=self.token)
        self.default_channel = default_channel or os.environ.get("SLACK_DEFAULT_CHANNEL")

    def send_notification(self, message, channel=None, max_retries=3):
        target_channel = channel or self.default_channel
        if not target_channel:
            raise ValueError("A target channel is required")

        for attempt in range(max_retries):
            try:
                response = self.client.chat_postMessage(
                    channel=target_channel,
                    text=message
                )
                return response
            except SlackApiError as e:
                if e.response.status_code == 429:
                    delay = int(e.response.headers.get('Retry-After', 1))
                    time.sleep(delay)
                else:
                    print(f"Error sending message: {e}")
                    raise e
        raise Exception("Max retries exceeded")

    def notify_contest(self, contest):
        message = self._format_contest_message(contest)
        return self.send_notification(message)

    def _format_contest_message(self, contest):
        return f"""
New eligible contest found!
Title: {contest.get('title', 'N/A')}
Entry Fee: ${contest.get('entry_fee', 'N/A')}
Total Prizes: ${contest.get('total_prizes', 'N/A')}
Current Entries: {contest.get('current_entries', 'N/A')}
Maximum Entries: {contest.get('maximum_entries', 'N/A')}
Link: https://www.draftkings.com/draft/contest/{contest.get('id', '')}
        """
