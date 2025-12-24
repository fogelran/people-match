from src.questions.question_service import QuestionService
from src.user_management.user import User


def test_next_question_tracks_unanswered():
    service = QuestionService(seed_questions=["Q1", "Q2"])
    user = User(name="Lena")

    assert service.next_question_for_user(user) == "Q1"
    service.record_answer(user, "Q1", True)
    assert service.next_question_for_user(user) == "Q2"
    service.record_answer(user, "Q2", False)
    assert service.next_question_for_user(user) == ""


def test_add_custom_question_adds_to_library_and_preferences():
    service = QuestionService(seed_questions=["Q1"])
    user = User(name="Nico")

    service.add_custom_question(user, "Q2", expected_answer=True)
    service.record_answer(user, "Q2", True)

    assert "Q2" in service.questions()
    assert user.asked_questions_with_expected_answer["Q2"] is True
    assert user.answers["Q2"] is True
