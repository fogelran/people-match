from .user import User


class PeopleSearch:
    DEFAULT_SEED_QUESTIONS = [
        "Are you looking for a long-term relationship?",
        "Do you want kids in the future?",
        "Do you enjoy outdoor activities?",
        "Are you a morning person?",
        "Do you like pets?",
    ]

    def __init__(self, seed_questions=None):
        self._users = {}
        self._questions = {}
        self._seed_questions = seed_questions or list(self.DEFAULT_SEED_QUESTIONS)
        for question in self._seed_questions:
            self._questions[question] = set()

    def add_user(self, name_id):
        if name_id not in self._users:
            self._users[name_id] = User(name=name_id)
        else:
            raise ValueError("Name '{0}' already exist".format(name_id))

    def get_user(self, name_id):
        if name_id not in self._users:
            raise KeyError(f"User '{name_id}' was not found")
        return self._users[name_id]

    def add_user_question(self, name_id, question, expected_answer):
        user = self.get_user(name_id)
        normalized_answer = bool(expected_answer)
        self._questions.setdefault(question, set())
        user.asked_questions_with_expected_answer[question] = normalized_answer

    def answer_question(self, name_id, question, answer):
        user = self.get_user(name_id)
        normalized_answer = bool(answer)
        self._questions.setdefault(question, set())
        user.answers[question] = normalized_answer
        self._questions[question].add(name_id)

    def get_user_answers(self, name_id):
        user = self.get_user(name_id)
        return dict(user.answers)

    def get_questions(self):
        return list(self._questions.keys())

    def get_questions_with_answered_status(self, name_id):
        user = self.get_user(name_id)
        return {question: (question in user.answers) for question in self._questions.keys()}

    def get_new_question_for_user(self, name_id):
        user = self.get_user(name_id)
        for question in self._questions.keys():
            if question not in user.answers:
                return question
        return ""

    def search(self, filters):
        """Find users who match every question/answer pair provided in filters."""
        normalized_filters = {q: bool(ans) for q, ans in filters.items()}
        matches = []
        for name, user in self._users.items():
            if all(user.answers.get(question) == expected for question, expected in normalized_filters.items()):
                matches.append(name)
        return matches

    def get_user_questions(self, name_id):
        user = self.get_user(name_id)
        return dict(user.asked_questions_with_expected_answer)
