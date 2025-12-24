from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set


@dataclass
class User:
    """Represents a participant in the people match system."""

    name: str
    profile_image_url: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    asked_questions_with_expected_answer: Dict[str, bool] = field(default_factory=dict)
    answers: Dict[str, bool] = field(default_factory=dict)
    skipped_questions: Set[str] = field(default_factory=set)

    def record_answer(self, question: str, answer: bool) -> None:
        self.answers[question] = bool(answer)

    def skip_question(self, question: str) -> None:
        self.skipped_questions.add(question)

    def clear_skip(self, question: str) -> None:
        self.skipped_questions.discard(question)

    def set_expected_answer(self, question: str, expected_answer: bool) -> None:
        self.asked_questions_with_expected_answer[question] = bool(expected_answer)
