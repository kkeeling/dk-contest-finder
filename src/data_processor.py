from typing import List, Dict, Any
from .database_manager import DatabaseManager
from .utils import with_spinner

print("DataProcessor module imported")

class ContestFilter:
    @staticmethod
    def filter_by_entrants(contests: List[Dict[str, Any]], max_entrants: int) -> List[Dict[str, Any]]:
        return [contest for contest in contests if contest.get('m', 0) < max_entrants]

    @staticmethod
    def filter_by_title(contests: List[Dict[str, Any]], title_keyword: str) -> List[Dict[str, Any]]:
        return [contest for contest in contests if title_keyword.lower() in contest.get('n', '').lower()]

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
        print("Initializing DataProcessor")
        self.db_manager = DatabaseManager()
        print("DataProcessor initialized")

    @with_spinner("Processing contests", spinner_type="dots")
    def process_contests(self, contests: List[Dict[str, Any]]) -> None:
        print(f"Processing {len(contests)} contests")
        filtered_contests = ContestFilter.apply_filters(contests)
        print(f"Filtered contests: {len(filtered_contests)}")
        
        processed_contests = []
        for contest in filtered_contests:
            print(f"Processing contest: {contest.get('id', 'Unknown ID')}")
            entrants = contest.pop('participants', [])
            print(f"Number of entrants: {len(entrants)}")
            analysis_result = EntrantAnalyzer.analyze_experience_levels(entrants)
            print(f"Analysis result: {analysis_result}")
            contest.update(analysis_result)

            if analysis_result['highest_experience_ratio'] < 0.3:
                contest['status'] = 'ready_to_enter'
            else:
                contest['status'] = 'processed'
            print(f"Contest status: {contest['status']}")

            processed_contests.append(contest)
            print(f"Inserting {len(entrants)} entrants for contest {contest['id']}")
            self.db_manager.batch_insert_entrants(contest['id'], entrants)

        print(f"Inserting {len(processed_contests)} processed contests")
        self.db_manager.batch_insert_contests(processed_contests)
        print("Finished processing contests")

    @with_spinner("Processing unprocessed contests", spinner_type="dots")
    def process_unprocessed_contests(self) -> None:
        print("Processing unprocessed contests")
        unprocessed_contests = self.db_manager.get_unprocessed_contests()
        print(f"Found {len(unprocessed_contests)} unprocessed contests")
        for contest in unprocessed_contests:
            print(f"Processing contest: {contest.get('id', 'Unknown ID')}")
            entrants = self.db_manager.get_contest_entrants(contest['id'])
            print(f"Number of entrants: {len(entrants)}")
            analysis_result = EntrantAnalyzer.analyze_experience_levels(entrants)
            print(f"Analysis result: {analysis_result}")
            contest.update(analysis_result)

            if analysis_result['highest_experience_ratio'] < 0.3:
                contest['status'] = 'ready_to_enter'
            else:
                contest['status'] = 'processed'
            print(f"Contest status: {contest['status']}")

            print(f"Updating status for contest {contest['id']}")
            self.db_manager.update_contest_status(contest['id'], contest['status'])
        print("Finished processing unprocessed contests")
