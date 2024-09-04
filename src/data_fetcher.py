import requests
import time
from typing import List, Dict, Any
import agentql
from playwright.sync_api import sync_playwright

class DataFetcher:
    BASE_URL = "https://www.draftkings.com/lobby/getcontests"
    CONTEST_DETAILS_URL = "https://www.draftkings.com/contest/detailspop?contestId={}"
    SUPPORTED_SPORTS = ["NFL", "NHL", "NBA", "MLB", "TEN", "SOC", "MMA", "GOL"]
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0

    def _construct_url(self, sport: str) -> str:
        return f"{self.BASE_URL}?sport={sport}"

    def _make_request(self, url: str) -> Dict[str, Any]:
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last_request)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return {}

    def fetch_contests(self, sport: str) -> List[Dict[str, Any]]:
        if sport not in self.SUPPORTED_SPORTS:
            print(f"Unsupported sport: {sport}")
            return []
        
        url = self._construct_url(sport)
        data = self._make_request(url)
        return data.get("Contests", [])

    def fetch_all_contests(self) -> Dict[str, List[Dict[str, Any]]]:
        all_contests = {}
        for sport in self.SUPPORTED_SPORTS:
            all_contests[sport] = self.fetch_contests(sport)
        return all_contests

    def fetch_contest_details(self, contest_id: str) -> Dict[str, Any]:
        url = self.CONTEST_DETAILS_URL.format(contest_id)
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = agentql.wrap(browser.new_page())
            page.goto(url)

            QUERY = """
            {
                contest_info {
                    title
                    entry_fee
                    total_prizes
                    entries {
                        current
                        maximum
                    }
                }
                participants[] {
                    username
                    experience_level
                }
            }
            """

            try:
                contest_data = page.query_data(QUERY)
                
                # Process participant data
                participants = contest_data.get('participants', [])
                processed_participants = []
                for participant in participants:
                    experience_level = self._map_experience_level(participant.get('experience_level', ''))
                    processed_participants.append({
                        'username': participant.get('username', ''),
                        'experience_level': experience_level
                    })

                contest_data['participants'] = processed_participants
                return contest_data
            except Exception as e:
                print(f"Error fetching contest details: {e}")
                return {}
            finally:
                browser.close()

    def _map_experience_level(self, level: str) -> int:
        level_map = {
            'beginner': 0,
            'low': 1,
            'medium': 2,
            'high': 3
        }
        return level_map.get(level.lower(), 0)
