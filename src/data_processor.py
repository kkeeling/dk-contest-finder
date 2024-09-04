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
        return [contest for contest in contests if contest['entries']['current'] < max_entrants and title_keyword.lower() in contest['title'].lower()]

class DataProcessor:
    @staticmethod
    def process_contests(contests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return ContestFilter.apply_filters(contests)
