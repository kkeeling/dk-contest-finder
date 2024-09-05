import time
import random
from typing import List, Dict, Any
import requests
from urllib.robotparser import RobotFileParser
from .utils import with_spinner

class DataFetcher:
    BASE_URL = "https://www.draftkings.com"
    LOBBY_URL = f"{BASE_URL}/lobby/getcontests"
    CONTEST_DETAILS_URL = f"{BASE_URL}/contest/detailspop?contestId={{}}"
    SUPPORTED_SPORTS = ["NFL"]
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.rp = RobotFileParser()
        self.rp.set_url(f"{self.BASE_URL}/robots.txt")
        self.rp.read()

    def _construct_url(self, sport: str) -> str:
        return f"{self.LOBBY_URL}?sport={sport}"

    def _respect_robots_txt(self, url: str) -> bool:
        return self.rp.can_fetch("*", url)

    def _wait_between_requests(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if time_since_last_request < delay:
            time.sleep(delay - time_since_last_request)
        else:
            time.sleep(0.01)  # Ensure a small delay even if enough time has passed
        
        self.last_request_time = time.time()

    @with_spinner("Fetching contests", spinner_type="dots")
    def fetch_contests(self, sport: str, limit: int = 100) -> List[Dict[str, Any]]:
        if sport not in self.SUPPORTED_SPORTS:
            print(f"Unsupported sport: {sport}")
            return []
        
        url = self._construct_url(sport)
        
        if not self._respect_robots_txt(url):
            print(f"Access to {url} disallowed by robots.txt")
            return []

        self._wait_between_requests()

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            contests = data.get("Contests", [])
            return contests[:limit]
        except requests.RequestException as e:
            print(f"Error fetching contests: {e}")
            return []

    @with_spinner("Fetching all contests", spinner_type="dots")
    def fetch_all_contests(self, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        all_contests = {}
        for sport in self.SUPPORTED_SPORTS:
            all_contests[sport] = self.fetch_contests(sport, limit)
        return all_contests

    @with_spinner("Fetching contest details", spinner_type="dots")
    def fetch_contest_details(self, contest_id: str) -> Dict[str, Any]:
        url = self.CONTEST_DETAILS_URL.format(contest_id)
        
        if not self._respect_robots_txt(url):
            print(f"Access to {url} disallowed by robots.txt")
            return {}

        self._wait_between_requests()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = agentql.wrap(browser.new_page())
            
            try:
                page.goto(url)
                QUERY = """
                {
                    contest_info
                    participants
                }
                """
                contest_data = page.query_data(QUERY)
                
                processed_data = {
                    'title': contest_data.get('contest_info', {}).get('title', ''),
                    'entry_fee': contest_data.get('contest_info', {}).get('entry_fee', 0),
                    'total_prizes': contest_data.get('contest_info', {}).get('total_prizes', 0),
                    'entries': {
                        'current': contest_data.get('contest_info', {}).get('entries', {}).get('current', 0),
                        'maximum': contest_data.get('contest_info', {}).get('entries', {}).get('maximum', 0)
                    },
                    'participants': []
                }

                # Process participant data
                participants = contest_data.get('participants', [])
                for participant in participants:
                    experience_level = self._map_experience_level(participant.get('experience_level', ''))
                    processed_data['participants'].append({
                        'username': participant.get('username', ''),
                        'experience_level': experience_level
                    })

                return processed_data
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
