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

    @with_spinner("Inserting or updating contest", spinner_type="dots")
    def insert_contest(self, contest: Dict[str, Any]) -> None:
        try:
            processed_contest = {
                'id': contest.get('id'),
                'title': contest.get('title'),
                'entry_fee': contest.get('entry_fee', 0),
                'total_prizes': contest.get('total_prizes', 0),
                'current_entries': contest.get('entries', {}).get('current', 0),
                'maximum_entries': contest.get('entries', {}).get('maximum', 0),
                'status': contest.get('status', 'unprocessed'),
                'highest_experience_ratio': contest.get('highest_experience_ratio'),
            }
            
            # Check if the contest already exists
            existing_contest = self.supabase.table('contests').select('id').eq('id', contest['id']).execute()
            
            if existing_contest.data:
                # Update existing contest
                self.supabase.table('contests').update(processed_contest).eq('id', contest['id']).execute()
                logger.info(f"Successfully updated contest {contest['id']}")
            else:
                # Insert new contest
                self.supabase.table('contests').insert(processed_contest).execute()
                logger.info(f"Successfully inserted contest {contest['id']}")
        except Exception as e:
            logger.error(f"Error inserting or updating contest {contest['id']}: {str(e)}")
            raise

    @with_spinner("Inserting contests", spinner_type="dots")
    def batch_insert_contests(self, contests: List[Dict[str, Any]], batch_size: int = 100) -> None:
        try:
            for contest in contests:
                self.insert_contest(contest)
            logger.info(f"Successfully inserted {len(contests)} contests")
        except Exception as e:
            logger.error(f"Error inserting contests: {str(e)}")
            raise

    @with_spinner("Inserting entrants", spinner_type="dots")
    def batch_insert_entrants(self, contest_id: str, entrants: List[Dict[str, Any]], batch_size: int = 100) -> None:
        try:
            inserted_count = 0
            for i in range(0, len(entrants), batch_size):
                batch = entrants[i:i+batch_size]
                for entrant in batch:
                    # Check if entrant already exists
                    existing_entrant = self.supabase.table("entrants").select("id").eq("contest_id", contest_id).eq("username", entrant["username"]).execute()
                    if not existing_entrant.data:
                        # Insert only if entrant doesn't exist
                        self.supabase.table("entrants").insert({"contest_id": contest_id, **entrant}).execute()
                        inserted_count += 1
            logger.info(f"Successfully inserted {inserted_count} new entrants for contest {contest_id}")
        except Exception as e:
            logger.error(f"Error inserting entrants for contest {contest_id}: {str(e)}")

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
