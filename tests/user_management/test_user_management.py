import pytest

from src.user_management.user_manager import UserManager


def test_register_user_with_optional_metadata():
    manager = UserManager()
    user = manager.register_user(
        "Aria",
        profile_image_url="https://images.example/aria.png",
        details={"city": "NYC", "hobby": "bouldering"},
    )

    assert user.name == "Aria"
    assert user.profile_image_url.endswith("aria.png")
    assert user.details["city"] == "NYC"
    assert user.details["hobby"] == "bouldering"


def test_re_register_updates_details_instead_of_duplication():
    manager = UserManager()
    first = manager.register_user("Milo", details={"city": "Austin"})
    second = manager.register_user("Milo", details={"role": "designer"}, profile_image_url="https://img/milo.jpg")

    assert first is second
    assert second.details["city"] == "Austin"
    assert second.details["role"] == "designer"
    assert second.profile_image_url == "https://img/milo.jpg"


def test_register_requires_name():
    manager = UserManager()
    with pytest.raises(ValueError):
        manager.register_user("")
