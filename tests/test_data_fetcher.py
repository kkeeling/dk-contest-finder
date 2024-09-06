import unittest
import requests
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from src.data_fetcher import DataFetcher

class TestDataFetcher(unittest.TestCase):

    def setUp(self):
        self.data_fetcher = DataFetcher()

    def test_construct_url(self):
        url = self.data_fetcher._construct_url("NFL")
        self.assertEqual(url, "https://www.draftkings.com/lobby/getcontests?sport=NFL")

    @patch('time.sleep')
    def test_wait_between_requests(self, mock_sleep):
        self.data_fetcher._wait_between_requests()
        mock_sleep.assert_called()

    @patch('requests.get')
    @patch('src.data_fetcher.DataFetcher._wait_between_requests')
    def test_fetch_contests(self, mock_wait, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"Contests": [{"id": 1, "name": "Test Contest"}]}
        mock_get.return_value = mock_response

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

    @patch('requests.Session.get')
    @patch('src.data_fetcher.DataFetcher._wait_between_requests')
    def test_fetch_contest_details(self, mock_wait, mock_get):
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <h2 data-test-id="contest-name">Test Contest</h2>
            <span class="contest-entries">5</span>
            <span data-test-id="contest-seats">10</span>
            <p data-test-id="contest-entry-fee">$10</p>
            <p data-test-id="contest-total-prizes">$100</p>
            <table id="entrants-table">
                <tr>
                    <td><span class="entrant-username">user1</span><span class="icon-experienced-user-1"></span></td>
                    <td><span class="entrant-username">user2</span><span class="icon-experienced-user-5"></span></td>
                </tr>
            </table>
        </html>
        '''
        mock_get.return_value = mock_response

        result = self.data_fetcher.fetch_contest_details("123")

        expected_result = {
            'title': 'Test Contest',
            'entry_fee': 10.0,
            'total_prizes': 100.0,
            'entries': {'current': 5, 'maximum': 10},
            'participants': [
                {'username': 'user1', 'experience_level': 1},
                {'username': 'user2', 'experience_level': 3}
            ]
        }
        self.assertEqual(result, expected_result)

    @patch('requests.Session.get')
    @patch('src.data_fetcher.DataFetcher._wait_between_requests')
    def test_fetch_contest_details_error(self, mock_wait, mock_get):
        mock_get.side_effect = requests.RequestException("Test error")
        result = self.data_fetcher.fetch_contest_details("123")
        self.assertEqual(result, {})

    def test_parse_currency(self):
        self.assertEqual(self.data_fetcher._parse_currency('$10'), 10.0)
        self.assertEqual(self.data_fetcher._parse_currency('$1,000'), 1000.0)
        self.assertEqual(self.data_fetcher._parse_currency('1,000'), 1000.0)

    def test_map_experience_level(self):
        self.assertEqual(self.data_fetcher._map_experience_level('0'), 0)
        self.assertEqual(self.data_fetcher._map_experience_level('1'), 1)
        self.assertEqual(self.data_fetcher._map_experience_level('2'), 2)
        self.assertEqual(self.data_fetcher._map_experience_level('3'), 3)
        self.assertEqual(self.data_fetcher._map_experience_level('4'), 3)
        self.assertEqual(self.data_fetcher._map_experience_level('5'), 3)
        self.assertEqual(self.data_fetcher._map_experience_level('unknown'), 0)

if __name__ == '__main__':
    unittest.main()
