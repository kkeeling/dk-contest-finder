import schedule
import time
import logging
import signal
import sys
from .data_fetcher import DataFetcher
from .data_processor import DataProcessor
from .database_manager import DatabaseManager
from .slack_notifier import SlackNotifier
from .utils import with_spinner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.data_processor = DataProcessor()
        self.db_manager = DatabaseManager()
        self.slack_notifier = SlackNotifier()
        self.is_running = False

    @with_spinner("Running contest finder", spinner_type="dots")
    def run_contest_finder(self):
        logger.info("Starting contest finder process")
        contests = self.data_fetcher.fetch_all_contests(limit=50)
        self.data_processor.process_contests(contests)
        eligible_contests = self.data_processor.process_unprocessed_contests()
        for contest in eligible_contests:
            self.slack_notifier.notify_contest(contest)
        logger.info("Contest finder process completed")

    def start(self):
        self.is_running = True
        schedule.every(5).minutes.do(self.run_contest_finder)
        logger.info("Scheduler started. Running contest finder every 5 minute.")
        
        # Run the contest finder immediately on start
        self.run_contest_finder()
        
        # while self.is_running:
        #     try:
        #         schedule.run_pending()
        #         time.sleep(1)
        #     except Exception as e:
        #         logger.error(f"Error in scheduler loop: {e}", exc_info=True)
        #         time.sleep(5)  # Wait for 5 seconds before retrying

    def stop(self):
        self.is_running = False
        schedule.clear()
        logger.info("Scheduler stopped.")

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}. Stopping scheduler.")
    scheduler.stop()
    sys.exit(0)

if __name__ == "__main__":
    scheduler = Scheduler()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"Unhandled exception in scheduler: {e}", exc_info=True)
    finally:
        scheduler.stop()
