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
    people_search.add_user_question(name_id="Ran", question="Do you like rainbows?")
    people_search.add_user_question(name_id="Ran", question="Do you like sex?")

    # assert
    assert len(people_search.get_user_questions(name_id="Ran")) == 2
    with pytest.raises(KeyError):
        people_search.add_user_question(name_id="Jessie", question="Do you like rainbows?")

