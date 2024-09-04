import unittest
from src.data_processor import ContestFilter, DataProcessor

class TestContestFilter(unittest.TestCase):
    def setUp(self):
        self.contests = [
            {"id": 1, "title": "NFL Double Up", "entries": {"current": 5, "maximum": 20}},
            {"id": 2, "title": "NBA Contest", "entries": {"current": 15, "maximum": 20}},
            {"id": 3, "title": "MLB Double Up", "entries": {"current": 8, "maximum": 20}},
        ]

    def test_filter_by_entrants(self):
        filtered = ContestFilter.filter_by_entrants(self.contests, 10)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["id"], 1)
        self.assertEqual(filtered[1]["id"], 3)

    def test_filter_by_title(self):
        filtered = ContestFilter.filter_by_title(self.contests, "Double Up")
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["id"], 1)
        self.assertEqual(filtered[1]["id"], 3)

    def test_apply_filters(self):
        filtered = ContestFilter.apply_filters(self.contests)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], 1)

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.data_processor = DataProcessor()
        self.contests = [
            {"id": 1, "title": "NFL Double Up", "entries": {"current": 5, "maximum": 20}},
            {"id": 2, "title": "NBA Contest", "entries": {"current": 15, "maximum": 20}},
            {"id": 3, "title": "MLB Double Up", "entries": {"current": 8, "maximum": 20}},
        ]

    def test_process_contests(self):
        processed = self.data_processor.process_contests(self.contests)
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0]["id"], 1)

if __name__ == '__main__':
    unittest.main()
