import time
import random
from typing import List, Dict, Any
import requests
from playwright.sync_api import sync_playwright
from playwright_dompath.dompath_sync import xpath_path
import agentql
from .utils import with_spinner

print("DataFetcher module imported")

class DataFetcher:
    BASE_URL = "https://www.draftkings.com"
    LOBBY_URL = f"{BASE_URL}/lobby/getcontests"
    CONTEST_DETAILS_URL = f"{BASE_URL}/contest/detailspop?contestId={{}}"
    SUPPORTED_SPORTS = ["NFL"]
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        print(f"Initializing DataFetcher with min_delay={min_delay}, max_delay={max_delay}")
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        print("DataFetcher initialized")

    def _construct_url(self, sport: str) -> str:
        return f"{self.LOBBY_URL}?sport={sport}"

    def _wait_between_requests(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if time_since_last_request < delay:
            wait_time = delay - time_since_last_request
            print(f"Waiting for {wait_time:.2f} seconds between requests")
            time.sleep(wait_time)
        else:
            print("Minimum delay already passed, adding small delay")
            time.sleep(0.01)  # Ensure a small delay even if enough time has passed
        
        self.last_request_time = time.time()

    @with_spinner("Fetching contests", spinner_type="dots")
    def fetch_contests(self, sport: str, limit: int = 100) -> List[Dict[str, Any]]:
        print(f"Fetching contests for sport: {sport}, limit: {limit}")
        if sport not in self.SUPPORTED_SPORTS:
            print(f"Unsupported sport: {sport}")
            return []
        
        url = self._construct_url(sport)
        print(f"Constructed URL: {url}")
        
        self._wait_between_requests()

        try:
            print(f"Sending GET request to {url}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            contests = data.get("Contests", [])
            print(f"Fetched {len(contests)} contests, returning {min(len(contests), limit)}")
            return contests[:limit]
        except requests.RequestException as e:
            print(f"Error fetching contests: {e}")
            return []

    @with_spinner("Fetching all contests", spinner_type="dots")
    def fetch_all_contests(self, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        print(f"Fetching all contests with limit: {limit}")
        all_contests = {}
        for sport in self.SUPPORTED_SPORTS:
            print(f"Fetching contests for sport: {sport}")
            all_contests[sport] = self.fetch_contests(sport, limit)
            print(f"Fetched {len(all_contests[sport])} contests for {sport}")
        print(f"Finished fetching all contests. Total sports: {len(all_contests)}")
        return all_contests

    @with_spinner("Fetching contest details", spinner_type="dots")
    def fetch_contest_details(self, contest_id: str) -> Dict[str, Any]:
        print(f"Fetching contest details for contest_id: {contest_id}")
        url = self.CONTEST_DETAILS_URL.format(contest_id)
        print(f"Contest details URL: {url}")
        
        self._wait_between_requests()

        with sync_playwright() as p:
            print("Launching Playwright browser")
            browser = p.chromium.launch(headless=True)
            page = agentql.wrap(browser.new_page())
            
            try:
                print(f"Navigating to URL: {url}")
                page.goto(url)
                QUERY = """
                    {
                        contest_info {
                            title
                            entry_fee
                            total_prizes
                        }
                        num_entries
                        total_entries
                        entrants_list(all attributes)[] {
                            entrant_username
                            icon
                        }
                    }                
                """

                print("Executing AgentQL query")
                contest_data = page.query_data(QUERY)
                print("AgentQL query executed successfully")
                
                processed_data = {
                    'title': contest_data.get('contest_info', {}).get('title', ''),
                    'entry_fee': contest_data.get('contest_info', {}).get('entry_fee', 0),
                    'total_prizes': contest_data.get('contest_info', {}).get('total_prizes', 0),
                    'entries': {
                        'current': contest_data.get('num_entries', 0),
                        'maximum': contest_data.get('total_entries', 0)
                    },
                    'participants': []
                }

                # Process participant data
                participants = contest_data.get('entrants_list', [])
                print(f"Processing {len(participants)} participants")
                for participant in participants:
                    experience_level = self._map_experience_level(participant.get('experience_level', ''))
                    processed_data['participants'].append({
                        'username': participant.get('entrant_username', ''),
                        'experience_level': experience_level
                    })

                print("Contest details processed successfully")
                return processed_data
            except Exception as e:
                print(f"Error fetching contest details: {e}")
                return {}
            finally:
                print("Closing Playwright browser")
                browser.close()

    def _map_experience_level(self, level: str) -> int:
        level_map = {
            'beginner': 0,
            'low': 1,
            'medium': 2,
            'high': 3
        }
        return level_map.get(level.lower(), 0)
