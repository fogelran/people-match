from typing import Dict, Iterable, Optional

from .user import User


class UserManager:
    """Handles creation and retrieval of user profiles."""

    def __init__(self):
        self._users: Dict[str, User] = {}

    def register_user(
        self,
        name: str,
        profile_image_url: Optional[str] = None,
        details: Optional[Dict[str, str]] = None,
    ) -> User:
        if not name:
            raise ValueError("User name is required")
        if name in self._users:
            existing = self._users[name]
            if profile_image_url:
                existing.profile_image_url = profile_image_url
            if details:
                existing.details.update(details)
            return existing

        new_user = User(name=name, profile_image_url=profile_image_url, details=details or {})
        self._users[name] = new_user
        return new_user

    def get_user(self, name: str) -> User:
        if name not in self._users:
            raise KeyError(f"User '{name}' was not found")
        return self._users[name]

    def all_users(self) -> Iterable[User]:
        return self._users.values()

    def has_user(self, name: str) -> bool:
        return name in self._users
