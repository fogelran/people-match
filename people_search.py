class User:
    pass

class PeopleSearch:
    def __init__(self):
        self._users = {}

    def add_user(self, name_id):
        if name_id not in self._users:
            self._users[name_id] = User()
        else:
            raise ValueError("Name '{0}' already exist".format(name_id))

