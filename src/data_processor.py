from typing import List, Dict, Any

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
    def analyze_experience_levels(entrants: List[Dict[str, Any]]) -> float:
        if not entrants:
            return 0.0
        highest_experience_count = sum(1 for entrant in entrants if entrant.get('experience_level', 0) == 3)
        return highest_experience_count / len(entrants)

class DataProcessor:
    @staticmethod
    def process_contests(contests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered_contests = ContestFilter.apply_filters(contests)
        for contest in filtered_contests:
            entrants = contest.get('participants', [])
            contest['high_experience_ratio'] = EntrantAnalyzer.analyze_experience_levels(entrants)
        return [contest for contest in filtered_contests if contest['high_experience_ratio'] < 0.3]
