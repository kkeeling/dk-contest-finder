import unittest
from unittest.mock import patch, MagicMock
from src.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager()
        self.db_manager.supabase = MagicMock()

    def test_insert_contests(self):
        contests = [{
            'id': '1',
            'title': 'Test Contest',
            'entry_fee': 10,
            'total_prizes': 100,
            'current_entries': 5,
            'maximum_entries': 10,
            'status': 'unprocessed',
            'highest_experience_ratio': 0.2
        }]
        self.db_manager.insert_contests(contests)
        self.db_manager.supabase.table.assert_called_with('contests')
        self.db_manager.supabase.table().insert.assert_called_with(contests[0])

    def test_insert_entrants(self):
        entrants = [{'username': 'user1', 'experience_level': 1}]
        self.db_manager.insert_entrants('1', entrants)
        self.db_manager.supabase.table.assert_called_with('entrants')
        self.db_manager.supabase.table().insert.assert_called_with({'contest_id': '1', 'username': 'user1', 'experience_level': 1})

    def test_get_unprocessed_contests(self):
        self.db_manager.supabase.table().select().eq().execute.return_value.data = [{'id': '1', 'status': 'unprocessed'}]
        result = self.db_manager.get_unprocessed_contests()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'unprocessed')

    def test_update_contest_status(self):
        self.db_manager.update_contest_status('1', 'processed')
        self.db_manager.supabase.table().update.assert_called_with({'status': 'processed'})
        self.db_manager.supabase.table().update().eq.assert_called_with('id', '1')

    def test_get_contest_entrants(self):
        self.db_manager.supabase.table().select().eq().execute.return_value.data = [{'contest_id': '1', 'username': 'user1'}]
        result = self.db_manager.get_contest_entrants('1')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['username'], 'user1')

    def test_batch_insert_contests(self):
        contests = [
            {'id': '1', 'title': 'Test Contest 1', 'entry_fee': 10, 'total_prizes': 100, 'entries': {'current': 5, 'maximum': 10}},
            {'id': '2', 'title': 'Test Contest 2', 'entry_fee': 20, 'total_prizes': 200, 'entries': {'current': 8, 'maximum': 15}}
        ]
        self.db_manager.batch_insert_contests(contests, batch_size=1)
        self.assertEqual(self.db_manager.supabase.table().insert.call_count, 2)
        
        # Check if the processed contests have all required fields
        calls = self.db_manager.supabase.table().insert.call_args_list
        for i, call in enumerate(calls):
            processed_contests = call[0][0]
            for processed_contest in processed_contests:
                self.assertIn('id', processed_contest)
                self.assertIn('title', processed_contest)
                self.assertIn('entry_fee', processed_contest)
                self.assertIn('total_prizes', processed_contest)
                self.assertIn('current_entries', processed_contest)
                self.assertIn('maximum_entries', processed_contest)
                self.assertIn('status', processed_contest)
                self.assertIn('highest_experience_ratio', processed_contest)

    def test_batch_insert_entrants(self):
        entrants = [{'username': 'user1', 'experience_level': 1}, {'username': 'user2', 'experience_level': 2}]
        self.db_manager.batch_insert_entrants('1', entrants, batch_size=1)
        self.assertEqual(self.db_manager.supabase.table().insert.call_count, 2)

    def test_query_contests(self):
        criteria = {'status': 'processed'}
        self.db_manager.supabase.table().select().eq().execute.return_value.data = [{'id': '1', 'status': 'processed'}]
        result = self.db_manager.query_contests(criteria)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'processed')

if __name__ == '__main__':
    unittest.main()
