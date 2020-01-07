import pytest

from people_search import PeopleSearch


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

    # assert
    with pytest.raises(KeyError):
        people_search.get_user(name_id="Jessie")
