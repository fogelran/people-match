from .user import User


class PeopleSearch:
    def __init__(self):
        self._users = {}
        self._questions = {}

    def add_user(self, name_id):
        if name_id not in self._users:
            self._users[name_id] = User()
            self._questions = {}
        else:
            raise ValueError("Name '{0}' already exist".format(name_id))

    def get_user(self, name_id):
        return self._users[name_id]

    def add_user_question(self, name_id, question, expected_answer):
        self._questions.setdefault(question, [])
        self._users[name_id].asked_questions_with_expected_answer[question] = expected_answer

    def get_user_questions(self, name_id):
        return self._users[name_id].asked_questions_with_expected_answer

    def get_new_question_for_user(self, name_id):
        for question, users in self._questions.items():
            if name_id not in users:
                return question
        return ""


