from typing import List, Dict, Any
from .database_manager import DatabaseManager
from .utils import with_spinner

class ContestFilter:
    @staticmethod
    def filter_by_entrants(contests: List[Dict[str, Any]], max_entrants: int) -> List[Dict[str, Any]]:
        return [contest for contest in contests if contest.get('entries', {}).get('current', 0) < max_entrants]

    @staticmethod
    def filter_by_title(contests: List[Dict[str, Any]], title_keyword: str) -> List[Dict[str, Any]]:
        return [contest for contest in contests if title_keyword.lower() in contest.get('title', '').lower()]

    @classmethod
    def apply_filters(cls, contests: List[Dict[str, Any]], max_entrants: int = 10, title_keyword: str = "Double Up") -> List[Dict[str, Any]]:
        filtered_by_entrants = set(contest['id'] for contest in cls.filter_by_entrants(contests, max_entrants))
        filtered_by_title = set(contest['id'] for contest in cls.filter_by_title(contests, title_keyword))
        filtered_ids = filtered_by_entrants.union(filtered_by_title)
        return [contest for contest in contests if contest['id'] in filtered_ids]

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
    def __init__(self):
        self.db_manager = DatabaseManager()

    @with_spinner("Processing contests", spinner_type="dots")
    def process_contests(self, contests: List[Dict[str, Any]]) -> None:
        filtered_contests = ContestFilter.apply_filters(contests)
        
        processed_contests = []
        for contest in filtered_contests:
            entrants = contest.pop('participants', [])
            analysis_result = EntrantAnalyzer.analyze_experience_levels(entrants)
            contest.update(analysis_result)

            if analysis_result['highest_experience_ratio'] < 0.3:
                contest['status'] = 'ready_to_enter'
            else:
                contest['status'] = 'processed'

            processed_contests.append(contest)
            self.db_manager.batch_insert_entrants(contest['id'], entrants)

        self.db_manager.batch_insert_contests(processed_contests)

    @with_spinner("Processing unprocessed contests", spinner_type="dots")
    def process_unprocessed_contests(self) -> None:
        unprocessed_contests = self.db_manager.get_unprocessed_contests()
        for contest in unprocessed_contests:
            entrants = self.db_manager.get_contest_entrants(contest['id'])
            analysis_result = EntrantAnalyzer.analyze_experience_levels(entrants)
            contest.update(analysis_result)

            if analysis_result['highest_experience_ratio'] < 0.3:
                contest['status'] = 'ready_to_enter'
            else:
                contest['status'] = 'processed'

            self.db_manager.update_contest_status(contest['id'], contest['status'])
