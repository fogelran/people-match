import pytest

from src.matching_logic.people_search import PeopleSearch


def test_search_returns_only_matching_users():
    people_search = PeopleSearch(seed_questions=["Q1", "Q2"])
    people_search.register_user("Alice")
    people_search.register_user("Bob")
    people_search.register_user("Carla")

    people_search.answer_question("Alice", "Q1", True)
    people_search.answer_question("Alice", "Q2", True)

    people_search.answer_question("Bob", "Q1", True)
    people_search.answer_question("Bob", "Q2", False)

    people_search.answer_question("Carla", "Q1", False)
    people_search.answer_question("Carla", "Q2", True)

    assert people_search.search({"Q1": True, "Q2": True}) == ["Alice"]
    assert set(people_search.search({"Q2": True})) == {"Alice", "Carla"}


def test_best_match_returns_top_candidate():
    people_search = PeopleSearch(seed_questions=["Travel?", "Spicy food?"])
    people_search.register_user("Seeker")
    people_search.add_user_question("Seeker", "Travel?", True)
    people_search.add_user_question("Seeker", "Spicy food?", False)

    people_search.register_user("Perfect")
    people_search.answer_question("Perfect", "Travel?", True)
    people_search.answer_question("Perfect", "Spicy food?", False)

    people_search.register_user("Close")
    people_search.answer_question("Close", "Travel?", True)
    people_search.answer_question("Close", "Spicy food?", True)

    assert people_search.best_match_for_user("Seeker") == "Perfect"

    with pytest.raises(KeyError):
        people_search.best_match_for_user("Unknown")
