import unittest
from unittest.mock import patch, MagicMock
import time
from src.scheduler import Scheduler

class TestScheduler(unittest.TestCase):
    @patch('src.scheduler.DataFetcher')
    @patch('src.scheduler.DataProcessor')
    @patch('src.scheduler.DatabaseManager')
    @patch('src.scheduler.SlackNotifier')
    def setUp(self, mock_slack, mock_db, mock_processor, mock_fetcher):
        self.mock_fetcher = mock_fetcher.return_value
        self.mock_processor = mock_processor.return_value
        self.mock_db = mock_db.return_value
        self.mock_slack = mock_slack.return_value
        self.scheduler = Scheduler()

    def test_run_contest_finder(self):
        # Mock the behavior of each component
        self.mock_fetcher.fetch_all_contests.return_value = [{'id': '1', 'title': 'Test Contest'}]
        self.mock_processor.process_contests.return_value = None
        self.mock_processor.process_unprocessed_contests.return_value = [{'id': '1', 'title': 'Test Contest', 'status': 'ready_to_enter'}]

        # Run the contest finder
        self.scheduler.run_contest_finder()

        # Assert that each method was called
        self.mock_fetcher.fetch_all_contests.assert_called_once()
        self.mock_processor.process_contests.assert_called_once()
        self.mock_processor.process_unprocessed_contests.assert_called_once()
        self.mock_slack.notify_contest.assert_called_once()

    @patch('src.scheduler.schedule')
    def test_start_and_stop(self, mock_schedule):
        # Mock the schedule.every() method
        mock_schedule.every.return_value.minutes.return_value.do.return_value = None

        # Start the scheduler
        self.scheduler.start()

        # Assert that the scheduler is running and the job is scheduled
        self.assertTrue(self.scheduler.is_running)
        mock_schedule.every.assert_called_once_with(5)
        mock_schedule.every().minutes.return_value.do.assert_called_once_with(self.scheduler.run_contest_finder)

        # Stop the scheduler
        self.scheduler.stop()

        # Assert that the scheduler is stopped and the schedule is cleared
        self.assertFalse(self.scheduler.is_running)
        mock_schedule.clear.assert_called_once()

    @patch('src.scheduler.schedule')
    @patch('src.scheduler.time')
    def test_scheduler_loop(self, mock_time, mock_schedule):
        # Mock the behavior to run the loop twice
        mock_time.sleep.side_effect = [None, Exception("Stop loop")]
        mock_schedule.run_pending.return_value = None

        # Start the scheduler
        with self.assertRaises(Exception):
            self.scheduler.start()

        # Assert that run_pending was called twice
        self.assertEqual(mock_schedule.run_pending.call_count, 2)

    def test_error_handling(self):
        # Mock an error in fetch_all_contests
        self.mock_fetcher.fetch_all_contests.side_effect = Exception("Test error")

        # Run the contest finder
        self.scheduler.run_contest_finder()

        # Assert that the error was handled and other methods were not called
        self.mock_fetcher.fetch_all_contests.assert_called_once()
        self.mock_processor.process_contests.assert_not_called()
        self.mock_processor.process_unprocessed_contests.assert_not_called()
        self.mock_slack.notify_contest.assert_not_called()

if __name__ == '__main__':
    unittest.main()
