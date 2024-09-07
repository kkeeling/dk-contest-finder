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

class DataFetcher:
    BASE_URL = "https://www.draftkings.com"
    LOBBY_URL = f"{BASE_URL}/lobby/getcontests"
    CONTEST_DETAILS_URL = f"{BASE_URL}/contest/detailspop?contestId={{}}"
    SUPPORTED_SPORTS = ["NFL"]
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0, max_workers: int = 5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.max_workers = max_workers
        self.session = requests.Session()

    def _construct_url(self, sport: str) -> str:
        return f"{self.LOBBY_URL}?sport={sport}"

    def _wait_between_requests(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if time_since_last_request < delay:
            wait_time = delay - time_since_last_request
            time.sleep(wait_time)
        else:
            time.sleep(0.01)  # Ensure a small delay even if enough time has passed
        
        self.last_request_time = time.time()

    @with_spinner("\nFetching contests for sport", spinner_type="dots")
    def fetch_contests(self, sport: str) -> List[Dict[str, Any]]:
        if sport not in self.SUPPORTED_SPORTS:
            return []
        
        url = self._construct_url(sport)
        self._wait_between_requests()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            contests = data.get("Contests", [])
            return contests
        except requests.RequestException as e:
            logger.error(f"Error fetching contests: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in fetch_contests: {e}", exc_info=True)
            return []

    @with_spinner("\nFetching all contests", spinner_type="dots")
    def fetch_all_contests(self) -> Dict[str, List[Dict[str, Any]]]:
        all_contests = {}
        for sport in self.SUPPORTED_SPORTS:
            try:
                all_contests[sport] = self.fetch_contests(sport)
            except Exception as e:
                logger.error(f"Error fetching contests for sport {sport}: {e}", exc_info=True)
        return all_contests

    @with_spinner("\nFetching contest details", spinner_type="dots")
    def fetch_contest_details(self, contest_id: str) -> Dict[str, Any]:
        url = self.CONTEST_DETAILS_URL.format(contest_id)
        self._wait_between_requests()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            
            contest_data = self._parse_contest_details(soup)
            if not contest_data:
                return {}
            return contest_data
        except requests.RequestException as e:
            logger.error(f"Error fetching contest details: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error in fetch_contest_details: {e}", exc_info=True)
            return {}

    def _parse_contest_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        try:
            contest_info = self._extract_contest_info(soup)
            participants = self._extract_participants(soup)
            
            if not contest_info or participants is None:
                return {}
            
            parsed_data = {
                'title': contest_info.get('name', ''),
                'entry_fee': self._parse_currency(contest_info.get('entry_fee', '0')),
                'total_prizes': self._parse_currency(contest_info.get('total_prizes', '0')),
                'entries': {
                    'current': int(contest_info.get('entries', '0')),
                    'maximum': int(contest_info.get('max_entries', '0'))
                },
                'participants': participants
            }
            return parsed_data
        except Exception as e:
            logger.error(f"Error in _parse_contest_details: {e}", exc_info=True)
            return {}

    def _extract_contest_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        contest_info = {}
        try:
            contest_info['name'] = soup.select_one('h2[data-test-id="contest-name"]').text.strip()
            contest_info['entries'] = soup.select_one('span.contest-entries').text.strip()
            contest_info['max_entries'] = soup.select_one('span[data-test-id="contest-seats"]').text.strip()
            contest_info['entry_fee'] = soup.select_one('p[data-test-id="contest-entry-fee"]').text.strip()
            contest_info['total_prizes'] = soup.select_one('p[data-test-id="contest-total-prizes"]').text.strip()
        except AttributeError as e:
            logger.error(f"Error extracting contest info: {e}")
        return contest_info

    def _extract_participants(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        participants = []
        try:
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
        except Exception as e:
            logger.error(f"Error extracting participants: {e}")
        return participants

    @with_spinner("\nFetching multiple contest details", spinner_type="dots")
    def fetch_multiple_contest_details(self, contest_ids: List[str]) -> List[Dict[str, Any]]:
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
        return results

    def _parse_contest_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        try:
            contest_info = self._extract_contest_info(soup)
            participants = self._extract_participants(soup)
            
            if not contest_info or not participants:
                return {}
            
            parsed_data = {
                'title': contest_info.get('name', ''),
                'entry_fee': self._parse_currency(contest_info.get('entry_fee', '0')),
                'total_prizes': self._parse_currency(contest_info.get('total_prizes', '0')),
                'entries': {
                    'current': self._parse_int_value(contest_info.get('entries', '0')),
                    'maximum': self._parse_int_value(contest_info.get('max_entries', '0'))
                },
                'participants': participants
            }
            return parsed_data
        except Exception as e:
            logger.error(f"Error in _parse_contest_details: {e}", exc_info=True)
            return {}

    def _parse_int_value(self, value: str) -> int:
        try:
            return int(value.replace(',', ''))
        except ValueError:
            if 'K' in value:
                return int(float(value.replace('K', '')) * 1000)
            elif 'M' in value:
                return int(float(value.replace('M', '')) * 1000000)
            else:
                logger.warning(f"Unable to parse int value: {value}")
                return 0

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
