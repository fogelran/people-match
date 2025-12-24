from typing import Dict, Iterable, List, Optional

from ..questions.question_service import QuestionService
from ..user_management.user import User
from ..user_management.user_manager import UserManager


class PeopleSearch:
    """Coordinates user management, questions, and matchmaking."""

    def __init__(
        self,
        seed_questions: Iterable[str] | None = None,
        user_manager: Optional[UserManager] = None,
        question_service: Optional[QuestionService] = None,
    ):
        self.user_manager = user_manager or UserManager()
        self.question_service = question_service or QuestionService(seed_questions)

    def register_user(
        self,
        name: str,
        profile_image_url: str | None = None,
        details: Optional[Dict[str, str]] = None,
    ) -> User:
        return self.user_manager.register_user(name, profile_image_url=profile_image_url, details=details)

    def get_user(self, name: str) -> User:
        return self.user_manager.get_user(name)

    def add_user_question(self, name: str, question: str, expected_answer: bool) -> None:
        user = self.get_user(name)
        self.question_service.add_custom_question(user, question, expected_answer)

    def answer_question(self, name: str, question: str, answer: bool) -> None:
        user = self.get_user(name)
        user.clear_skip(question)
        self.question_service.record_answer(user, question, answer)

    def skip_question(self, name: str, question: str) -> None:
        user = self.get_user(name)
        user.skip_question(question)

    def get_user_answers(self, name: str) -> Dict[str, bool]:
        user = self.get_user(name)
        return dict(user.answers)

    def get_skipped_questions(self, name: str) -> set[str]:
        user = self.get_user(name)
        return set(user.skipped_questions)

    def get_questions(self) -> List[str]:
        return self.question_service.questions()

    def get_questions_with_answered_status(self, name: str) -> Dict[str, bool]:
        user = self.get_user(name)
        return self.question_service.question_answered_status(user)

    def get_new_question_for_user(self, name: str) -> str:
        user = self.get_user(name)
        return self.question_service.next_question_for_user(user)

    def get_user_questions(self, name: str) -> Dict[str, bool]:
        user = self.get_user(name)
        return dict(user.asked_questions_with_expected_answer)

    def search(self, filters: Dict[str, bool]) -> List[str]:
        """Find users who match every question/answer pair provided in filters."""
        normalized_filters = {question: bool(answer) for question, answer in filters.items()}
        matches: List[str] = []
        for user in self.user_manager.all_users():
            if all(user.answers.get(question) == expected for question, expected in normalized_filters.items()):
                matches.append(user.name)
        return matches

    def best_match_for_user(self, name: str) -> str:
        seeker = self.get_user(name)
        preferences = seeker.asked_questions_with_expected_answer
        if not preferences:
            return ""

        best_candidate = ""
        best_score = -1.0

        for candidate in self.user_manager.all_users():
            if candidate.name == seeker.name:
                continue
            score, total = self._score_candidate(candidate, preferences)
            if total == 0:
                continue
            ratio = score / total
            if ratio > best_score:
                best_score = ratio
                best_candidate = candidate.name
        return best_candidate

    @staticmethod
    def _score_candidate(candidate: User, preferences: Dict[str, bool]) -> tuple[int, int]:
        score = 0
        total = 0
        for question, expected_answer in preferences.items():
            total += 1
            if candidate.answers.get(question) == expected_answer:
                score += 1
        return score, total
