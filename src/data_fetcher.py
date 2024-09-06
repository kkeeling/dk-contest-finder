import time
import random
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import with_spinner
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("DataFetcher module imported")

class DataFetcher:
    BASE_URL = "https://www.draftkings.com"
    LOBBY_URL = f"{BASE_URL}/lobby/getcontests"
    CONTEST_DETAILS_URL = f"{BASE_URL}/contest/detailspop?contestId={{}}"
    SUPPORTED_SPORTS = ["NFL"]
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0, max_workers: int = 5):
        logger.info(f"Initializing DataFetcher with min_delay={min_delay}, max_delay={max_delay}, max_workers={max_workers}")
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.max_workers = max_workers
        self.session = requests.Session()
        logger.info("DataFetcher initialized")

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
        logger.info(f"Fetching contest details for contest_id: {contest_id}")
        url = self.CONTEST_DETAILS_URL.format(contest_id)
        logger.debug(f"Contest details URL: {url}")
        
        self._wait_between_requests()

        try:
            logger.debug(f"Sending GET request to {url}")
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            contest_data = self._parse_contest_details(soup)
            logger.info("Contest details parsed successfully")
            return contest_data
        except requests.RequestException as e:
            logger.error(f"Error fetching contest details: {e}")
            return {}

    @with_spinner("Fetching multiple contest details", spinner_type="dots")
    def fetch_multiple_contest_details(self, contest_ids: List[str]) -> List[Dict[str, Any]]:
        logger.info(f"Fetching details for {len(contest_ids)} contests")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_id = {executor.submit(self.fetch_contest_details, contest_id): contest_id for contest_id in contest_ids}
            results = []
            for future in as_completed(future_to_id):
                contest_id = future_to_id[future]
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    logger.error(f'{contest_id} generated an exception: {exc}')
        logger.info(f"Fetched details for {len(results)} contests")
        return results

    def _parse_contest_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        contest_info = self._extract_contest_info(soup)
        participants = self._extract_participants(soup)
        
        return {
            'title': contest_info.get('name', ''),
            'entry_fee': self._parse_currency(contest_info.get('entry_fee', '0')),
            'total_prizes': self._parse_currency(contest_info.get('total_prizes', '0')),
            'entries': {
                'current': int(contest_info.get('entries', '0')),
                'maximum': int(contest_info.get('max_entries', '0'))
            },
            'participants': participants
        }

    def _extract_contest_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        return {
            'name': soup.select_one('h2[data-test-id="contest-name"]').text.strip(),
            'entries': soup.select_one('span.contest-entries').text.strip(),
            'max_entries': soup.select_one('span[data-test-id="contest-seats"]').text.strip(),
            'entry_fee': soup.select_one('p[data-test-id="contest-entry-fee"]').text.strip(),
            'total_prizes': soup.select_one('p[data-test-id="contest-total-prizes"]').text.strip(),
        }

    def _extract_participants(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        participants = []
        entrants_table = soup.select_one('table#entrants-table')
        
        if entrants_table:
            for cell in entrants_table.select('td:not(.empty-user)'):
                username = cell.select_one('span.entrant-username').text.strip()
                experience_icon = cell.select_one('span[class^="icon-experienced-user-"]')
                experience_level = self._map_experience_level(experience_icon['class'][0].split('-')[-1] if experience_icon else '0')
                
                participants.append({
                    'username': username,
                    'experience_level': experience_level
                })
        
        return participants

    def _parse_currency(self, value: str) -> float:
        return float(value.replace('$', '').replace(',', ''))

    def _map_experience_level(self, level: str) -> int:
        level_map = {
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 3,
            '5': 3
        }
        return level_map.get(level, 0)
