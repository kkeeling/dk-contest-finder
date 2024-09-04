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
        filtered_contests = cls.filter_by_entrants(contests, max_entrants)
        filtered_contests = cls.filter_by_title(filtered_contests, title_keyword)
        return filtered_contests

class DataProcessor:
    def __init__(self):
        self.contest_filter = ContestFilter()

    def process_contests(self, contests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.contest_filter.apply_filters(contests)
