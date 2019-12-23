import pytest

from people_search import PeopleSearch


def test_create_people_search():
    people_search = PeopleSearch()


def test_add_user():
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")
    with pytest.raises(ValueError):
        people_search.add_user(name_id="Ran")


def test_cannotp_add_user():
    people_search = PeopleSearch()
    people_search.add_user(name_id="Ran")
