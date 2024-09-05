import os
import logging
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

logger = logging.getLogger(__name__)

# Load environment variables from .env.local
load_dotenv('.env.local')

class SlackNotifier:
    def __init__(self, token=None):
        self.token = token or os.getenv("SLACK_BOT_TOKEN") or "test_token"
        self.client = WebClient(token=self.token)
        self.channel = "__dk_contests"

    def send_notification(self, message, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = self.client.chat_postMessage(
                    channel=self.channel,
                    text=message
                )
                logger.info(f"Message sent successfully to channel {self.channel}")
                return response
            except SlackApiError as e:
                if e.response.status_code == 429:
                    delay = int(e.response.headers.get('Retry-After', 1))
                    logger.warning(f"Rate limited. Retrying in {delay} seconds.")
                    time.sleep(delay)
                else:
                    logger.error(f"Error sending message: {e}")
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
Highest Experience Ratio: {contest.get('highest_experience_ratio', 'N/A'):.2%}
Link: https://www.draftkings.com/draft/contest/{contest.get('id', '')}
        """

    def test_connection(self):
        try:
            response = self.client.auth_test()
            logger.info(f"Successfully connected to Slack. Bot name: {response['bot_id']}")
            return True
        except SlackApiError as e:
            logger.error(f"Error testing Slack connection: {e}")
            return False
