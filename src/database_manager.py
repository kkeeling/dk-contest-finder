import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict, Any
from .utils import with_spinner

load_dotenv('.env.local')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.supabase = None
        self.initialize_supabase()

    def initialize_supabase(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env.local file")
        self.supabase: Client = create_client(url, key)

    def get_supabase(self) -> Client:
        if not self.supabase:
            self.initialize_supabase()
        return self.supabase

    def insert_contests(self, contests: List[Dict[str, Any]]) -> None:
        try:
            for contest in contests:
                self.supabase.table('contests').insert(contest).execute()
            logger.info(f"Successfully inserted {len(contests)} contests")
        except Exception as e:
            logger.error(f"Error inserting contests: {str(e)}")
            raise

    def insert_entrants(self, contest_id: str, entrants: List[Dict[str, Any]]) -> None:
        try:
            for entrant in entrants:
                entrant['contest_id'] = contest_id
                self.supabase.table('entrants').insert(entrant).execute()
            logger.info(f"Successfully inserted {len(entrants)} entrants for contest {contest_id}")
        except Exception as e:
            logger.error(f"Error inserting entrants for contest {contest_id}: {str(e)}")
            raise

    def get_unprocessed_contests(self) -> List[Dict[str, Any]]:
        try:
            response = self.supabase.table('contests').select('*').eq('status', 'unprocessed').execute()
            logger.info(f"Retrieved {len(response.data)} unprocessed contests")
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving unprocessed contests: {str(e)}")
            raise

    def update_contest_status(self, contest_id: str, status: str) -> None:
        try:
            self.supabase.table('contests').update({'status': status}).eq('id', contest_id).execute()
            logger.info(f"Updated status of contest {contest_id} to {status}")
        except Exception as e:
            logger.error(f"Error updating status of contest {contest_id}: {str(e)}")
            raise

    def get_contest_entrants(self, contest_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.supabase.table('entrants').select('*').eq('contest_id', contest_id).execute()
            logger.info(f"Retrieved {len(response.data)} entrants for contest {contest_id}")
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving entrants for contest {contest_id}: {str(e)}")
            raise

    @with_spinner("Inserting contests", spinner_type="dots")
    def batch_insert_contests(self, contests: List[Dict[str, Any]], batch_size: int = 100) -> None:
        try:
            for i in range(0, len(contests), batch_size):
                batch = contests[i:i+batch_size]
                processed_batch = []
                for contest in batch:
                    processed_contest = {
                        'id': contest.get('id'),
                        'title': contest.get('title'),
                        'entry_fee': contest.get('entry_fee', 0),  # Default to 0 if not provided
                        'total_prizes': contest.get('total_prizes'),
                        'current_entries': contest.get('entries', {}).get('current'),
                        'maximum_entries': contest.get('entries', {}).get('maximum'),
                        'status': contest.get('status', 'unprocessed'),
                        'highest_experience_ratio': contest.get('highest_experience_ratio'),
                    }
                    processed_batch.append(processed_contest)
                self.supabase.table('contests').insert(processed_batch).execute()
            logger.info(f"Successfully batch inserted {len(contests)} contests")
        except Exception as e:
            logger.error(f"Error batch inserting contests: {str(e)}")
            raise

    @with_spinner("Inserting entrants", spinner_type="dots")
    def batch_insert_entrants(self, contest_id: str, entrants: List[Dict[str, Any]], batch_size: int = 100) -> None:
        try:
            for i in range(0, len(entrants), batch_size):
                batch = entrants[i:i+batch_size]
                for entrant in batch:
                    entrant['contest_id'] = contest_id
                self.supabase.table('entrants').insert(batch).execute()
            logger.info(f"Successfully batch inserted {len(entrants)} entrants for contest {contest_id}")
        except Exception as e:
            logger.error(f"Error batch inserting entrants for contest {contest_id}: {str(e)}")
            raise

    @with_spinner("Querying contests", spinner_type="dots")
    def query_contests(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            query = self.supabase.table('contests').select('*')
            for key, value in criteria.items():
                query = query.eq(key, value)
            response = query.execute()
            logger.info(f"Retrieved {len(response.data)} contests based on criteria")
            return response.data
        except Exception as e:
            logger.error(f"Error querying contests: {str(e)}")
            raise
