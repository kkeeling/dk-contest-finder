# This file will contain the Database Manager component implementation
import os
from supabase import create_client, Client
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def insert_contests(self, contests: List[Dict[str, Any]]) -> None:
        for contest in contests:
            self.supabase.table('contests').insert(contest).execute()

    def insert_entrants(self, contest_id: str, entrants: List[Dict[str, Any]]) -> None:
        for entrant in entrants:
            entrant['contest_id'] = contest_id
            self.supabase.table('entrants').insert(entrant).execute()

    def get_unprocessed_contests(self) -> List[Dict[str, Any]]:
        response = self.supabase.table('contests').select('*').eq('status', 'unprocessed').execute()
        return response.data

    def update_contest_status(self, contest_id: str, status: str) -> None:
        self.supabase.table('contests').update({'status': status}).eq('id', contest_id).execute()

    def get_contest_entrants(self, contest_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table('entrants').select('*').eq('contest_id', contest_id).execute()
        return response.data
