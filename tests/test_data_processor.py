import unittest
from src.data_processor import ContestFilter, DataProcessor, EntrantAnalyzer

class TestContestFilter(unittest.TestCase):
    def setUp(self):
        self.contests = [
            {"id": 1, "title": "NFL Double Up", "entries": {"current": 50, "maximum": 1000}},
            {"id": 2, "title": "NFL 3-Player", "entries": {"current": 1, "maximum": 3}},
            {"id": 3, "title": "NFL 5-Player", "entries": {"current": 2, "maximum": 5}},
            {"id": 4, "title": "NFL Millionaire Maker", "entries": {"current": 10000, "maximum": 1000000}},
        ]

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
        self.assertEqual(filtered[0]["id"], 1)
        self.assertEqual(filtered[1]["id"], 2)
        self.assertEqual(filtered[2]["id"], 3)
class TestEntrantAnalyzer(unittest.TestCase):
    def test_analyze_experience_levels(self):
        entrants = [
            {"experience_level": 0},
            {"experience_level": 1},
            {"experience_level": 2},
            {"experience_level": 3},
            {"experience_level": 3},
        ]
        ratio = EntrantAnalyzer.analyze_experience_levels(entrants)
        self.assertEqual(ratio, 0.4)

    def test_analyze_experience_levels_empty(self):
        ratio = EntrantAnalyzer.analyze_experience_levels([])
        self.assertEqual(ratio, 0.0)

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

    def test_process_contests(self):
        processed = self.data_processor.process_contests(self.contests)
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0]["id"], 2)
        self.assertLess(processed[0]["high_experience_ratio"], 0.3)

if __name__ == '__main__':
    unittest.main()
