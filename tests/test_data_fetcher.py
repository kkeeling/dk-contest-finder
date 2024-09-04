import unittest
from unittest.mock import patch
from src.data_fetcher import DataFetcher

class TestDataFetcher(unittest.TestCase):

    def setUp(self):
        self.data_fetcher = DataFetcher()

    def test_construct_url(self):
        url = self.data_fetcher._construct_url("NFL")
        self.assertEqual(url, "https://www.draftkings.com/lobby/getcontests?sport=NFL")

    @patch('src.data_fetcher.requests.get')
    def test_make_request(self, mock_get):
        mock_get.return_value.json.return_value = {"Contests": []}
        mock_get.return_value.raise_for_status.return_value = None
        
        result = self.data_fetcher._make_request("https://test.com")
        self.assertEqual(result, {"Contests": []})

    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_fetch_contests(self, mock_make_request):
        mock_make_request.return_value = {"Contests": [{"id": 1, "name": "Test Contest"}]}
        
        result = self.data_fetcher.fetch_contests("NFL")
        self.assertEqual(result, [{"id": 1, "name": "Test Contest"}])

    def test_fetch_contests_unsupported_sport(self):
        result = self.data_fetcher.fetch_contests("UNSUPPORTED")
        self.assertEqual(result, [])

    @patch('src.data_fetcher.DataFetcher.fetch_contests')
    def test_fetch_all_contests(self, mock_fetch_contests):
        mock_fetch_contests.return_value = [{"id": 1, "name": "Test Contest"}]
        
        result = self.data_fetcher.fetch_all_contests()
        self.assertEqual(len(result), len(DataFetcher.SUPPORTED_SPORTS))
        for sport in DataFetcher.SUPPORTED_SPORTS:
            self.assertIn(sport, result)
            self.assertEqual(result[sport], [{"id": 1, "name": "Test Contest"}])

if __name__ == '__main__':
    unittest.main()
