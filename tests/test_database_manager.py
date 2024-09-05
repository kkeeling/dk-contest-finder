import unittest
from unittest.mock import patch, MagicMock
from src.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager()

    @patch('src.database_manager.create_client')
    def test_init(self, mock_create_client):
        mock_create_client.return_value = MagicMock()
        db_manager = DatabaseManager()
        self.assertIsNotNone(db_manager.supabase)

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_insert_contests(self, mock_supabase):
        contests = [{'id': '1', 'title': 'Test Contest'}]
        self.db_manager.insert_contests(contests)
        mock_supabase.table.assert_called_with('contests')
        mock_supabase.table().insert.assert_called_with(contests[0])

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_insert_entrants(self, mock_supabase):
        entrants = [{'username': 'user1', 'experience_level': 1}]
        self.db_manager.insert_entrants('1', entrants)
        mock_supabase.table.assert_called_with('entrants')
        mock_supabase.table().insert.assert_called_with({'contest_id': '1', 'username': 'user1', 'experience_level': 1})

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_get_unprocessed_contests(self, mock_supabase):
        mock_supabase.table().select().eq().execute.return_value.data = [{'id': '1', 'status': 'unprocessed'}]
        result = self.db_manager.get_unprocessed_contests()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'unprocessed')

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_update_contest_status(self, mock_supabase):
        self.db_manager.update_contest_status('1', 'processed')
        mock_supabase.table().update.assert_called_with({'status': 'processed'})
        mock_supabase.table().update().eq.assert_called_with('id', '1')

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_get_contest_entrants(self, mock_supabase):
        mock_supabase.table().select().eq().execute.return_value.data = [{'contest_id': '1', 'username': 'user1'}]
        result = self.db_manager.get_contest_entrants('1')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['username'], 'user1')

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_batch_insert_contests(self, mock_supabase):
        contests = [{'id': '1', 'title': 'Test Contest 1'}, {'id': '2', 'title': 'Test Contest 2'}]
        self.db_manager.batch_insert_contests(contests, batch_size=1)
        self.assertEqual(mock_supabase.table().insert.call_count, 2)

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_batch_insert_entrants(self, mock_supabase):
        entrants = [{'username': 'user1'}, {'username': 'user2'}]
        self.db_manager.batch_insert_entrants('1', entrants, batch_size=1)
        self.assertEqual(mock_supabase.table().insert.call_count, 2)

    @patch('src.database_manager.DatabaseManager.supabase')
    def test_query_contests(self, mock_supabase):
        criteria = {'status': 'processed'}
        mock_supabase.table().select().eq().execute.return_value.data = [{'id': '1', 'status': 'processed'}]
        result = self.db_manager.query_contests(criteria)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'processed')

if __name__ == '__main__':
    unittest.main()
