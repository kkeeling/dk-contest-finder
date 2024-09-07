from typing import List, Dict, Any
from .database_manager import DatabaseManager
from .utils import with_spinner

class ContestFilter:
    @staticmethod
    def filter_by_entrants(contests: Dict[str, List[Dict[str, Any]]], max_entrants: int) -> Dict[str, List[Dict[str, Any]]]:
        return {sport: [contest for contest in sport_contests if contest.get('m', 0) <= max_entrants]
                for sport, sport_contests in contests.items()}

    @staticmethod
    def filter_by_title(contests: Dict[str, List[Dict[str, Any]]], title_keyword: str) -> Dict[str, List[Dict[str, Any]]]:
        return {sport: [contest for contest in sport_contests if title_keyword.lower() in contest.get('n', '').lower()]
                for sport, sport_contests in contests.items()}

    @staticmethod
    def filter_by_entry_fee(contests: Dict[str, List[Dict[str, Any]]], max_entry_fee: float) -> Dict[str, List[Dict[str, Any]]]:
        return {sport: [contest for contest in sport_contests if contest.get('a', 0) <= max_entry_fee]
                for sport, sport_contests in contests.items()}

    @staticmethod
    def filter_by_game_type(contests: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        return {sport: [contest for contest in sport_contests if contest.get('gameType') in ['Classic', 'Showdown Captain Mode']]
                for sport, sport_contests in contests.items()}

    @classmethod
    def apply_filters(cls, contests: Dict[str, List[Dict[str, Any]]], max_entrants: int = 5, title_keyword: str = "Double Up", max_entry_fee: float = 50.0) -> Dict[str, List[Dict[str, Any]]]:
        filtered_by_entrants = {sport: set(contest['id'] for contest in sport_contests)
                                for sport, sport_contests in cls.filter_by_entrants(contests, max_entrants).items()}
        
        filtered_contests = {}
        for sport in contests.keys():
            filtered_ids = filtered_by_entrants.get(sport, set())
            filtered_contests[sport] = [
                contest for contest in contests[sport] 
                if contest['id'] in filtered_ids 
                and "casual" not in contest.get('n', '').lower() 
                and "beginner" not in contest.get('n', '').lower()
                and "satellite" not in contest.get('n', '').lower()
                and "madden" not in contest.get('n', '').lower()
                and float(contest.get('a', 0)) <= max_entry_fee
                and contest.get('gameType') in ['Classic', 'Showdown Captain Mode']
            ]
        
        return filtered_contests

class EntrantAnalyzer:
    @staticmethod
    def categorize_experience_level(level: int) -> int:
        if level == 0:
            return 0  # beginner
        elif level == 1:
            return 1  # low
        elif level == 2:
            return 2  # medium
        else:
            return 3  # highest

    @staticmethod
    def analyze_experience_levels(entrants: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not entrants:
            return {"highest_experience_ratio": 0.0, "experience_distribution": {}}

        experience_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        total_entrants = len(entrants)

        for entrant in entrants:
            level = EntrantAnalyzer.categorize_experience_level(entrant.get('experience_level', 0))
            experience_counts[level] += 1

        highest_experience_ratio = experience_counts[3] / total_entrants

        experience_distribution = {
            level: count / total_entrants
            for level, count in experience_counts.items()
        }

        return {
            "highest_experience_ratio": highest_experience_ratio,
            "experience_distribution": experience_distribution
        }

class DataProcessor:
    def __init__(self, data_fetcher):
        self.db_manager = DatabaseManager()
        self.data_fetcher = data_fetcher
        self.blacklisted_usernames = set(["lakergreat2", "theleafnode", "glamrock"])  # Add your blacklisted usernames here

    def has_blacklisted_user(self, entrants: List[Dict[str, Any]]) -> bool:
        return any(entrant['username'] in self.blacklisted_usernames for entrant in entrants)

    @with_spinner("\nProcessing contests", spinner_type="dots")
    def process_contests(self, contests: Dict[str, List[Dict[str, Any]]]) -> None:
        filtered_contests = ContestFilter.apply_filters(contests)

        total_contests = sum(len(sport_contests) for sport_contests in filtered_contests.values())
        print(f', Found {total_contests} contests')
        for sport, sport_contests in filtered_contests.items():
            for contest in sport_contests:
                contest_details = self.data_fetcher.fetch_contest_details(contest['id'])
                if not contest_details:
                    continue
                
                contest.update(contest_details)
                entrants = contest.pop('participants', [])

                # Check for blacklisted usernames
                if self.has_blacklisted_user(entrants):
                    contest['highest_experience_ratio'] = 1.0
                    contest['status'] = 'scooped'
                else:
                    analysis_result = EntrantAnalyzer.analyze_experience_levels(entrants)
                    contest.update(analysis_result)
                    contest['status'] = 'ready_to_enter' if analysis_result['highest_experience_ratio'] <= 0.8 else 'processed'

                self.db_manager.insert_contest(contest)

                if entrants:
                    self.db_manager.batch_insert_entrants(contest['id'], entrants)

    @with_spinner("\nProcessing unprocessed contests", spinner_type="dots")
    def process_unprocessed_contests(self) -> None:
        unprocessed_contests = self.db_manager.get_unprocessed_contests()
        for contest in unprocessed_contests:
            entrants = self.db_manager.get_contest_entrants(contest['id'])
            
            if self.has_blacklisted_user(entrants):
                contest['highest_experience_ratio'] = 1.0
                contest['status'] = 'processed'
            else:
                analysis_result = EntrantAnalyzer.analyze_experience_levels(entrants)
                contest.update(analysis_result)
                contest['status'] = 'ready_to_enter' if analysis_result['highest_experience_ratio'] <= 0.8 else 'processed'

            self.db_manager.update_contest_status(contest['id'], contest['status'])
