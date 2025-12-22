class User:
    """Represents a participant in the people search system."""

    def __init__(self, name=None):
        # The name is stored for convenience; PeopleSearch uses the key as the source of truth.
        self.name = name
        # Maps question -> expected answer the user is looking for in a match (True/False).
        self.asked_questions_with_expected_answer = {}
        # Maps question -> the user's answer (True/False).
        self.answers = {}
