import time
import random
from typing import List, Dict, Any
import agentql
from playwright.sync_api import sync_playwright
from urllib.robotparser import RobotFileParser

class DataFetcher:
    BASE_URL = "https://www.draftkings.com"
    LOBBY_URL = f"{BASE_URL}/lobby/getcontests"
    CONTEST_DETAILS_URL = f"{BASE_URL}/contest/detailspop?contestId={{}}"
    SUPPORTED_SPORTS = ["NFL", "NHL", "NBA", "MLB", "TEN", "SOC", "MMA", "GOL"]
    
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
        
        self.last_request_time = time.time()

    def fetch_contests(self, sport: str) -> List[Dict[str, Any]]:
        if sport not in self.SUPPORTED_SPORTS:
            print(f"Unsupported sport: {sport}")
            return []
        
        url = self._construct_url(sport)
        
        if not self._respect_robots_txt(url):
            print(f"Access to {url} disallowed by robots.txt")
            return []

        self._wait_between_requests()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = agentql.wrap(browser.new_page())
            
            try:
                page.goto(url)
                data = page.query_data("{Contests[]}")
                return data.get("Contests", [])
            except Exception as e:
                print(f"Error fetching contests: {e}")
                return []
            finally:
                browser.close()

    def fetch_all_contests(self) -> Dict[str, List[Dict[str, Any]]]:
        all_contests = {}
        for sport in self.SUPPORTED_SPORTS:
            all_contests[sport] = self.fetch_contests(sport)
        return all_contests

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
