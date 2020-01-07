from .user import User


class PeopleSearch:
    def __init__(self):
        self._users = {}
        self._questions = {}

    def add_user(self, name_id):
        if name_id not in self._users:
            self._users[name_id] = User()
            self._questions[name_id] = []
        else:
            raise ValueError("Name '{0}' already exist".format(name_id))

    def get_user(self, name_id):
        return self._users[name_id]

    def add_user_question(self, name_id, question):
        self._questions[name_id].append(question)

    def get_user_questions(self, name_id):
        return self._questions[name_id]
