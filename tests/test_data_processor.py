import unittest
from unittest.mock import MagicMock, patch
from src.data_processor import ContestFilter, DataProcessor, EntrantAnalyzer
from src.database_manager import DatabaseManager
from src.data_fetcher import DataFetcher

class TestContestFilter(unittest.TestCase):
    def setUp(self):
        self.contests = {
            "NFL": [
                {"id": 1, "n": "NFL Double Up", "m": 1000, "a": 10},
                {"id": 2, "n": "NFL 3-Player", "m": 3, "a": 5},
                {"id": 3, "n": "NFL 5-Player", "m": 5, "a": 20},
                {"id": 4, "n": "NFL Millionaire Maker", "m": 1000000, "a": 100},
            ]
        }

    def test_filter_by_entrants(self):
        filtered = ContestFilter.filter_by_entrants(self.contests, 10)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["id"], 2)
        self.assertEqual(filtered[1]["id"], 3)

    def test_filter_by_title(self):
        filtered = ContestFilter.filter_by_title(self.contests, "Double Up")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], 1)

        filtered = ContestFilter.filter_by_title(self.contests, "3-Player")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], 2)

        filtered = ContestFilter.filter_by_title(self.contests, "5-Player")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], 3)

    def test_apply_filters(self):
        filtered = ContestFilter.apply_filters(self.contests)
        self.assertEqual(len(filtered), 3)
        filtered_ids = {contest["id"] for contest in filtered}
        self.assertEqual(filtered_ids, {1, 2, 3})
        self.assertNotIn(4, filtered_ids)  # "NFL Millionaire Maker" (not Double Up and more than 10 entrants)

class TestEntrantAnalyzer(unittest.TestCase):
    def test_analyze_experience_levels(self):
        entrants = [
            {"experience_level": 0},
            {"experience_level": 1},
            {"experience_level": 2},
            {"experience_level": 3},
            {"experience_level": 3},
        ]
        result = EntrantAnalyzer.analyze_experience_levels(entrants)
        self.assertAlmostEqual(result['highest_experience_ratio'], 0.4)
        self.assertEqual(result['experience_distribution'], {0: 0.2, 1: 0.2, 2: 0.2, 3: 0.4})

    def test_analyze_experience_levels_empty(self):
        result = EntrantAnalyzer.analyze_experience_levels([])
        self.assertEqual(result['highest_experience_ratio'], 0.0)
        self.assertEqual(result['experience_distribution'], {})

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.data_processor = DataProcessor()
        self.contests = [
            {
                "id": 1,
                "title": "NFL Double Up",
                "entries": {"current": 50, "maximum": 1000},
                "participants": [
                    {"experience_level": 3},
                    {"experience_level": 3},
                    {"experience_level": 2},
                    {"experience_level": 1},
                    {"experience_level": 0},
                ]
            },
            {
                "id": 2,
                "title": "NFL 3-Player",
                "entries": {"current": 1, "maximum": 3},
                "participants": [
                    {"experience_level": 0},
                    {"experience_level": 1},
                    {"experience_level": 2},
                ]
            },
            {
                "id": 3,
                "title": "NFL 5-Player",
                "entries": {"current": 2, "maximum": 5},
                "participants": [
                    {"experience_level": 3},
                    {"experience_level": 3},
                    {"experience_level": 3},
                    {"experience_level": 3},
                    {"experience_level": 3},
                ]
            },
        ]

    @patch.object(DatabaseManager, 'insert_contests')
    @patch.object(DatabaseManager, 'insert_entrants')
    def test_process_contests(self, mock_insert_entrants, mock_insert_contests):
        self.data_processor.process_contests(self.contests)
        mock_insert_contests.assert_called()
        mock_insert_entrants.assert_called()

    @patch.object(DatabaseManager, 'get_unprocessed_contests')
    @patch.object(DatabaseManager, 'get_contest_entrants')
    @patch.object(DatabaseManager, 'update_contest_status')
    def test_process_unprocessed_contests(self, mock_update_status, mock_get_entrants, mock_get_unprocessed):
        mock_get_unprocessed.return_value = [self.contests[1]]  # Return the contest with id 2
        mock_get_entrants.return_value = self.contests[1]['participants']
        
        self.data_processor.process_unprocessed_contests()
        
        mock_get_unprocessed.assert_called_once()
        mock_get_entrants.assert_called_once_with(2)
        mock_update_status.assert_called_once_with(2, 'ready_to_enter')

if __name__ == '__main__':
    unittest.main()
