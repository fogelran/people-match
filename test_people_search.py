import pytest

from src.people_search import PeopleSearch


def test_add_and_retrieve_user():
    people_search = PeopleSearch(seed_questions=["A?"])
    people_search.add_user(name_id="Ran")

    retrieved = people_search.get_user(name_id="Ran")
    assert retrieved.name == "Ran"


def test_when_adding_duplicate_user_then_throw():
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")

    with pytest.raises(ValueError):
        people_search.add_user(name_id="Ran")


def test_when_requesting_non_exist_user_then_throw():
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")

    people_search.get_user(name_id="Ran")
    with pytest.raises(KeyError):
        people_search.get_user(name_id="Jessie")


def test_when_adding_user_question_then_added():
    people_search = PeopleSearch(seed_questions=["Seed question?"])
    people_search.add_user(name_id="Ran")

    people_search.add_user_question(name_id="Ran", question="Do you like rainbows?", expected_answer=True)
    people_search.add_user_question(name_id="Ran", question="Do you know python?", expected_answer=False)

    assert len(people_search.get_user_questions(name_id="Ran")) == 2
    assert "Do you like rainbows?" in people_search.get_questions()
    with pytest.raises(KeyError):
        people_search.add_user_question(name_id="Jessie", question="Do you like rainbows?", expected_answer=True)


def test_get_new_question_cycles_through_unanswered():
    people_search = PeopleSearch(seed_questions=["Seed?"])
    people_search.add_user(name_id="Ran")
    people_search.add_user_question(name_id="Ran", question="Do you like rainbows?", expected_answer=True)

    # unanswered questions are returned first
    first = people_search.get_new_question_for_user(name_id="Ran")
    assert first == "Seed?"

    people_search.answer_question(name_id="Ran", question="Seed?", answer=False)
    second = people_search.get_new_question_for_user(name_id="Ran")
    assert second == "Do you like rainbows?"

    people_search.answer_question(name_id="Ran", question="Do you like rainbows?", answer=True)
    assert people_search.get_new_question_for_user(name_id="Ran") == ""


def test_search_returns_only_matching_users():
    people_search = PeopleSearch(
        seed_questions=["Are you a morning person?", "Do you like pets?"],
    )
    people_search.add_user("Alice")
    people_search.add_user("Bob")
    people_search.add_user("Carla")

    people_search.answer_question("Alice", "Are you a morning person?", True)
    people_search.answer_question("Alice", "Do you like pets?", True)

    people_search.answer_question("Bob", "Are you a morning person?", True)
    people_search.answer_question("Bob", "Do you like pets?", False)

    people_search.answer_question("Carla", "Are you a morning person?", False)
    people_search.answer_question("Carla", "Do you like pets?", True)

    morning_pet_lovers = people_search.search(
        {"Are you a morning person?": True, "Do you like pets?": True}
    )
    assert morning_pet_lovers == ["Alice"]

    pet_lovers = people_search.search({"Do you like pets?": True})
    assert set(pet_lovers) == {"Alice", "Carla"}

    assert people_search.search({"Are you a morning person?": False}) == ["Carla"]
