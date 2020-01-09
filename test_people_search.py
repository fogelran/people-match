import pytest

from src.people_search import PeopleSearch


def test_create_people_search():
    people_search = PeopleSearch()


def test_add_user():
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")


def test_when_adding_duplicate_user_then_throw():
    # prepare
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")

    # assert
    with pytest.raises(ValueError):
        people_search.add_user(name_id="Ran")


def test_when_requesting_non_exist_user_then_throw():
    # prepare
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")

    # test
    people_search.get_user(name_id="Ran")

    with pytest.raises(KeyError):
        people_search.get_user(name_id="Jessie")


def test_when_adding_user_question_then_added():
    # prepare
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")

    # test
    people_search.add_user_question(name_id="Ran", question="Do you like rainbows?", expected_answer=True)
    people_search.add_user_question(name_id="Ran", question="Do you know python?", expected_answer=False)

    # assert
    assert len(people_search.get_user_questions(name_id="Ran")) == 2
    with pytest.raises(KeyError):
        people_search.add_user_question(name_id="Jessie", question="Do you like rainbows?", expected_answer=True)


def test_when_user_ask_for_question_and_question_pool_empty_then_get_empty_string():
    # prepare
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")

    # test
    question_from_empty_pool = people_search.get_new_question_for_user(name_id="Ran")

    # assert
    assert question_from_empty_pool == ""


def test_when_user_ask_for_question_then_get_one_from_the_pool():
    # prepare
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")
    user_example_question = "Do you like rainbows?"

    # test
    people_search.add_user_question(name_id="Ran", question=user_example_question, expected_answer=True)
    user_received_question = people_search.get_new_question_for_user(name_id="Ran")

    # assert
    assert user_received_question == user_example_question

