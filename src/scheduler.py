import schedule
import time
import logging
from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
from src.database_manager import DatabaseManager
from src.slack_notifier import SlackNotifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.data_processor = DataProcessor()
        self.db_manager = DatabaseManager()
        self.slack_notifier = SlackNotifier()

    def run_contest_finder(self):
        try:
            logger.info("Starting contest finder process")
            contests = self.data_fetcher.fetch_all_contests()
            self.data_processor.process_contests(contests)
            eligible_contests = self.data_processor.process_unprocessed_contests()
            for contest in eligible_contests:
                self.slack_notifier.notify_contest(contest)
            logger.info("Contest finder process completed")
        except Exception as e:
            logger.error(f"Error in contest finder: {e}")

    def start(self):
        schedule.every(5).minutes.do(self.run_contest_finder)
        logger.info("Scheduler started. Running contest finder every 5 minutes.")
        
        while True:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        schedule.clear()
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    scheduler = Scheduler()
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping scheduler.")
        scheduler.stop()
