from typing import List, Dict, Any
from .database_manager import DatabaseManager
from .utils import with_spinner

print("DataProcessor module imported")

class ContestFilter:
    @staticmethod
    def filter_by_entrants(contests: Dict[str, List[Dict[str, Any]]], max_entrants: int) -> Dict[str, List[Dict[str, Any]]]:
        return {sport: [contest for contest in sport_contests if contest.get('m', 0) < max_entrants]
                for sport, sport_contests in contests.items()}

    @staticmethod
    def filter_by_title(contests: Dict[str, List[Dict[str, Any]]], title_keyword: str) -> Dict[str, List[Dict[str, Any]]]:
        return {sport: [contest for contest in sport_contests if title_keyword.lower() in contest.get('n', '').lower()]
                for sport, sport_contests in contests.items()}

    @classmethod
    def apply_filters(cls, contests: Dict[str, List[Dict[str, Any]]], max_entrants: int = 10, title_keyword: str = "Double Up") -> Dict[str, List[Dict[str, Any]]]:
        filtered_by_entrants = {sport: set(contest['id'] for contest in sport_contests)
                                for sport, sport_contests in cls.filter_by_entrants(contests, max_entrants).items()}
        filtered_by_title = {sport: set(contest['id'] for contest in sport_contests)
                             for sport, sport_contests in cls.filter_by_title(contests, title_keyword).items()}
        
        filtered_contests = {}
        for sport in contests.keys():
            filtered_ids = filtered_by_entrants.get(sport, set()).union(filtered_by_title.get(sport, set()))
            filtered_contests[sport] = [contest for contest in contests[sport] if contest['id'] in filtered_ids]
        
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
    def __init__(self):
        print("Initializing DataProcessor")
        self.db_manager = DatabaseManager()
        print("DataProcessor initialized")

    @with_spinner("Processing contests", spinner_type="dots")
    def process_contests(self, contests: Dict[str, List[Dict[str, Any]]]) -> None:
        print(f"Processing contests for {len(contests)} sports")
        filtered_contests = ContestFilter.apply_filters(contests)
        print(f"Filtered contests: {sum(len(sport_contests) for sport_contests in filtered_contests.values())}")
        
        processed_contests = []
        for sport, sport_contests in filtered_contests.items():
            print(f"Processing {len(sport_contests)} contests for {sport}")
            for contest in sport_contests:
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
