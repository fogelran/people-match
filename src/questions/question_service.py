from typing import Dict, Iterable, List, Set

from ..user_management.user import User


class QuestionService:
    """Stores shared questions and orchestrates answers and preferences."""

    DEFAULT_SEED_QUESTIONS = [
        "Are you looking for a long-term relationship?",
        "Do you want kids in the future?",
        "Do you enjoy outdoor activities?",
        "Are you a morning person?",
        "Do you like pets?",
    ]

    def __init__(self, seed_questions: Iterable[str] | None = None):
        self._questions: Dict[str, Set[str]] = {}
        for question in seed_questions or self.DEFAULT_SEED_QUESTIONS:
            self._questions[question] = set()

    def add_custom_question(self, user: User, question: str, expected_answer: bool) -> None:
        normalized_answer = bool(expected_answer)
        self._questions.setdefault(question, set())
        user.set_expected_answer(question, normalized_answer)

    def record_answer(self, user: User, question: str, answer: bool) -> None:
        normalized_answer = bool(answer)
        self._questions.setdefault(question, set())
        user.record_answer(question, normalized_answer)
        self._questions[question].add(user.name)

    def questions(self) -> List[str]:
        return list(self._questions.keys())

    def unanswered_questions_for_user(self, user: User) -> List[str]:
        return [question for question in self._questions if question not in user.answers]

    def next_question_for_user(self, user: User) -> str:
        unanswered = self.unanswered_questions_for_user(user)
        return unanswered[0] if unanswered else ""

    def question_answered_status(self, user: User) -> Dict[str, bool]:
        return {question: (question in user.answers) for question in self._questions}
